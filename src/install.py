from sys import exit

def __setup_redis():
	import re, os

	redis_port = int(os.environ['REDIS_PORT'])
	redis_conf = []
	redis_replace = [
		("daemonize no", "no", "yes"),
		("pidfile /var/run/redis.pid", "redis", "redis_%d" % redis_port),
		("port 6379", "6379", str(redis_port)),
		("logfile \"\"", "\"\"", "/var/log/redis_%d.log" % redis_port),
		("dir ./", "./", "/var/redis/%d" % redis_port)
	]

	try:
		with open(os.path.join(os.path.expanduser('~'), "redis-stable", "redis.conf"), 'rb') as r:
			for line in r.read().splitlines():
				for rr in redis_replace:
					if line == rr[0]:
						line = line.replace(rr[1], rr[2])
						
						print "replaced: %s" % line
						break

				redis_conf.append(line)
	except Exception as e:
		print "could not build redis config from template"
		print e, type(e)

		return False

	try:
		with open(os.path.join(os.path.expanduser('~'), "config", "%d.conf" % redis_port), 'wb+') as r:
			r.write("\n".join(redis_conf))

		return True
	except Exception as e:
		print "could not save %d.conf" % redis_port
		print e, type(e)

	return False

if __name__ == "__main__":
	exit(0 if __setup_redis() else -1)