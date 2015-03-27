#! /bin/bash

THIS_DIR=`pwd`
REDIS_PORT=${REDIS_PORT:=echo 6379}

wget -O $THIS_DIR/lib/redis-stable.tar.gz http://download.redis.io/redis-stable.tar.gz
cd $THIS_DIR/lib
tar -xvzf redis-stable.tar.gz
rm redis-stable.tar.gz

cd redis-stable
make
sudo cp src/redis-server /usr/local/bin
sudo cp src/redis-cli /usr/local/bin
sudo mkdir /etc/redis
sudo mkdir -p /var/redis/$REDIS_PORT
sudo cp utils/redis_init_script /etc/init.d/redis_$REDIS_PORT

cd $THIS_DIR