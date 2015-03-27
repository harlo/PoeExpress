#! /bin/bash

source ~/.bash_profile

sudo service ssh start
python proofofexistence/app.py start --config=~/config/poe.config.json
if ([ $? -eq 0 ]); then
	echo "proofofexistence is up and running!"
	tail -f /dev/null
else
	echo "Failed to start proofofexistence."
fi