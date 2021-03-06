import os, json, yaml
from sys import argv, exit

from dutils.conf import DUtilsKey, DUtilsKeyDefaults, build_config, BASE_DIR, append_to_config, save_config, __load_config
from dutils.conf import DUtilsTransforms as transforms
from dutils.dutils import build_routine, build_dockerfile

API_PORT = 8080
REDIS_PORT = 6379

DEFAULT_PORTS = [22]
DEFAULT_ADMIN_PATH = "admin"
DEFAULT_ADMIN_EMAIL = "harlo.holmes@gmail.com"
DEFAULT_SENDER_EMAIL = "hello@camera-v.org"

def init_d(with_config):
	global API_PORT, REDIS_PORT, DEFAULT_SENDER_EMAIL, DEFAULT_ADMIN_PATH, DEFAULT_ADMIN_EMAIL

	conf_keys = [
		DUtilsKeyDefaults['USER'],
		DUtilsKeyDefaults['USER_PWD'],
		DUtilsKeyDefaults['IMAGE_NAME'],
		DUtilsKey("API_PORT", "POE api port", API_PORT, str(API_PORT), transforms['PORT_TO_INT']),
		DUtilsKey("REDIS_PORT", "POE redis port", REDIS_PORT, str(REDIS_PORT), transforms['PORT_TO_INT']),
		DUtilsKey("SECRET_ADMIN_PATH", "POE api's secret admin path", \
			DEFAULT_ADMIN_PATH, DEFAULT_ADMIN_PATH, None),
		DUtilsKey("PAYMENT_ADDRESS", "Bitcoin payment address", "None", "None", None),
		DUtilsKey("ADMIN_EMAIL", "Admin's email address", \
			DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_EMAIL, None),
		DUtilsKey("DEFAULT_SENDER_EMAIL", "Default email to send from", \
			DEFAULT_SENDER_EMAIL, DEFAULT_SENDER_EMAIL, None)
	]

	config = build_config(conf_keys, with_config)

	from dutils.dutils import get_docker_exe, get_docker_ip, validate_private_key

	docker_exe = get_docker_exe()
	if docker_exe is None:
		return False

	save_config(config, with_config=with_config)

	WORKING_DIR = BASE_DIR if with_config is None else os.path.dirname(with_config)
	if not validate_private_key(os.path.join(WORKING_DIR, "%s.privkey" % config['IMAGE_NAME']), with_config):
		return False
	
	res, config = append_to_config({
		'DOCKER_EXE' : docker_exe, 
		'DOCKER_IP' : get_docker_ip()
	}, return_config=True, with_config=with_config)

	print config

	if not res:
		return False

	from fabric.api import settings, local
	for sf in ["config", config['SECRET_ADMIN_PATH']]:
		with settings(warn_only=True):
			if not os.path.exists(os.path.join(BASE_DIR, "src", sf)):
				local("mkdir %s" % os.path.join(BASE_DIR, "src", sf))

	directives = ["export %s=%d" % (d, int(config[d])) for d in ['API_PORT', 'REDIS_PORT']]
	
	export_config = {}
	
	export_config_keys = ["ADMIN_EMAIL", "DEFAULT_SENDER_EMAIL", "SECRET_ADMIN_PATH", "BLOCKCHAIN_WALLET_GUID", \
		"BLOCKCHAIN_PASSWORD_1", "BLOCKCHAIN_PASSWORD_2", "CALLBACK_SECRET", \
		"BLOCKCHAIN_ENCRYPTED_WALLET", "PAYMENT_PRIVATE_KEY", "PAYMENT_ADDRESS"]

	for key in export_config_keys:
		if key in config.keys():
			export_config[key] = config[key]

	with open(os.path.join(BASE_DIR, "src", "config", "poe.config.json"), 'wb+') as EC:
		EC.write(json.dumps(export_config))

	from dutils.conf import get_directive

	print argv
	pgp_key = get_directive(argv, "pgpkey")
	print "PGP FOUND AT: %s" % pgp_key

	if pgp_key is not None and os.path.exists(pgp_key):
		with settings(warn_only=True):
			local("cp %s %s" % (pgp_key, os.path.join(BASE_DIR, "src", config['SECRET_ADMIN_PATH'])))

	import re
	with open(os.path.join(BASE_DIR, "src", "proofofexistence", "cron.yaml"), 'rb') as CRON:
		try:
			jobs = [{'command' : "curl -X GET http://localhost:%d%s" % (config['API_PORT'], job['url']), \
				'comment' : job['description'], \
				'unit' : re.findall(r'every\s\d+\s(\w+)', job['schedule'].strip())[0], \
				'frequency' : int(re.findall(r'every\s(\d+)\s\w+', job['schedule'].strip())[0])} for job in yaml.load(CRON.read())['cron']]

			print jobs

			from dutils.dutils import build_cron_job
			if not build_cron_job(jobs, dest_d=os.path.join(BASE_DIR, "src", "config")):
				return False

		except Exception as e:
			print e, type(e)
			print "COULD NOT WRITE CRON!!!\nContinue without the cron file?"
			
			from fabric.operations import prompt
			if prompt("[Y/n] : ") == "n":
				return False

	from dutils.dutils import generate_init_routine, build_bash_profile
	return build_bash_profile(directives, os.path.join(BASE_DIR, "src")) and \
		build_dockerfile("Dockerfile.init", config) and \
		generate_init_routine(config, with_config=with_config)

def build_d(with_config):
	res, config = append_to_config({'COMMIT_TO' : "poe_express"}, return_config=True, with_config=with_config)

	if not res:
		return False

	global DEFAULT_PORTS
	import operator

	mapped_ports = [config['API_PORT']]
	DEFAULT_PORTS = operator.add(DEFAULT_PORTS, mapped_ports)
	DEFAULT_PORTS = operator.add(DEFAULT_PORTS, [config['REDIS_PORT']])

	res, config = append_to_config({
		'DEFAULT_PORTS' : " ".join([str(p) for p in DEFAULT_PORTS]),
		'MAPPED_PORTS' : mapped_ports,
		'PUBLISH_PORTS' : mapped_ports
	}, return_config=True, with_config=with_config)

	if not res:
		return False

	from dutils.dutils import generate_build_routine
	return build_dockerfile("Dockerfile.build", config) and \
		generate_build_routine(config, with_config=with_config)

def commit_d(with_config):
	try:
		config = __load_config(with_config=with_config)
	except Exception as e:
		print e, type(e)

	if config is None:
		return False

	print config

	from dutils.dutils import generate_run_routine, generate_shutdown_routine, finalize_assets
	return generate_run_routine(config, src_dirs=["proofofexistence"], with_config=with_config) and \
		generate_shutdown_routine(config, with_config=with_config) and \
		finalize_assets(with_config=with_config)

def update_d(with_config):
	return build_dockerfile("Dockerfile.update", __load_config(with_config=with_config))

if __name__ == "__main__":
	res = False
	with_config = None if len(argv) == 2 else argv[2]

	if argv[1] == "init":
		res = init_d(with_config)
	elif argv[1] == "build":
		res = build_d(with_config)
	elif argv[1] == "commit":
		res = commit_d(with_config)
	elif argv[1] == "finish":
		res = True
	elif argv[1] == "update":
		res = update_d(with_config)
	
	print "RESULT from %s: " % argv[1], res 
	exit(0 if res else -1)