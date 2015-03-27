#! /bin/bash

source ~/.bash_profile

function do_update {
	cd $1
	git fetch --all
	git reset --hard origin/master
	git pull origin master
}

do_update ~/proofofexistence