#! /bin/bash

THIS_DIR=`pwd`

# Create virtualenv
virtualenv venv
source venv/bin/activate

pip install -r requirements.txt

# install redis
which redis-server
if ([ $? -eq 1 ]); then
	echo "have to install redis first!"
	./install_redis.sh
fi

deactivate venv