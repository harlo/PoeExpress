#! /bin/bash

source ~/.bash_profile

sudo service ssh start
sudo cron -f &

python proofofexistence/app.py start --base-dir=~/config
if ([ $? -eq 0 ]); then
	echo "proofofexistence is up and running!"
else
	echo "Failed to start proofofexistence."
fi

tail -f /dev/null