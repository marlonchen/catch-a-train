#!/bin/bash
redis-cli -h redis SET "apikey:123" "enabled"
echo "Redis initialized with test data!"
