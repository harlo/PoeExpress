#! /bin/bash

source ~/.bash_profile
REDIS_PID_FILE=/var/run/redis_$REDIS_PORT.pid

sudo service ssh start
sudo cron -f &

if [ -f $REDIS_PID_FILE ]; then
	sudo rm $REDIS_PID_FILE
fi

sudo service redis_$REDIS_PORT start

python proofofexistence/app.py start --base-dir=~/config
if ([ $? -eq 0 ]); then
	echo "proofofexistence is up and running!"
else
	echo "Failed to start proofofexistence."
fi

tail -f /dev/null