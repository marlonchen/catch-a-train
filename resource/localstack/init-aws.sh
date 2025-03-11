#!/bin/bash

# table notif_record_table
awslocal dynamodb create-table \
    --table-name notif_record_table \
    --attribute-definitions \
        AttributeName=hash_key,AttributeType=S \
        AttributeName=sort_key,AttributeType=S \
    --key-schema \
        AttributeName=hash_key,KeyType=HASH \
        AttributeName=sort_key,KeyType=RANGE \
    --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1

# table notif_schedule_table with ttl and stream
awslocal dynamodb create-table \
    --table-name notif_schedule_table \
    --attribute-definitions AttributeName=hash_key,AttributeType=S \
    --key-schema AttributeName=hash_key,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
    --stream-specification StreamEnabled=true,StreamViewType=OLD_IMAGE
awslocal dynamodb update-time-to-live \
    --table-name notif_schedule_table \
    --time-to-live-specification Enabled=true,AttributeName=ttl
