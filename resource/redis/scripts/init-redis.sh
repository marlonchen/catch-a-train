#!/bin/bash

redis-server --daemonize yes && sleep 1

redis-cli < ./init-data.redis
redis-cli save
redis-cli shutdown

redis-server

echo "Redis initialized with test data!"
