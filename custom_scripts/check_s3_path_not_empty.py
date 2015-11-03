#!/usr/bin/python

# Script for checking if an S3 Path has uploaded objects inside

import boto.opsworks
import boto.s3
import argparse
from boto.s3.connection import OrdinaryCallingFormat

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--region',
                    default='us-east-1',
                    type=str, help='AWS region')
parser.add_argument('-o', '--opsworks_region',
                    default='us-east-1',
                    type=str, help='Opsworks region endpoint')
parser.add_argument('-s', '--shipper_opsworks_layer_id',
                    default='9f1f1fa0-6a52-4227-8c54-76dd17873a27',
                    type=str, help='Opsworks ID of the Shipper Layer')
parser.add_argument('-e', '--redis_opsworks_layer_id',
                    default='5175c391-cb2a-49bb-be19-4d588d35d430',
                    type=str, help='Opsworks ID of the Redis Layer')
parser.add_argument('-i', '--indexer_opsworks_layer_id',
                    default='9cafbed2-a248-40a4-8b9d-0a68a8629771',
                    type=str, help='Opsworks ID of the Indexer Layer')
parser.add_argument('-sb', '--source_s3_bucket',
                    default='roy-testbucket1',
                    type=str, help='Source S3 bucket for shipper')
parser.add_argument('-sp', '--source_s3_path',
                    default='test1/',
                    type=str, help='Path inside source S3 bucket for shipper')
args = parser.parse_args()
region = args.region
opsworks_region = args.opsworks_region
s3_bucket = args.source_s3_bucket
path = args.source_s3_path
shipper_opsworks_layer_id = args.shipper_opsworks_layer_id
redis_opsworks_layer_id = args.redis_opsworks_layer_id
indexer_opsworks_layer_id = args.indexer_opsworks_layer_id


# Check status of ELK instances
def check_instance_status(opswork, opsworks_layer_id, layername):
    instances = opswork.describe_instances(layer_id=opsworks_layer_id)
    for key, value in instances.items():
        for i in range(0, len(value)):
            status = value[i].get('Status')
            opswork_id = value[i].get('InstanceId')

            if status != 'stopped':
                # Instance should be in stopped state to start pipeline
                print layername + ' instance with opsworks id ' + \
                    opswork_id + ' ' + \
                    ' should be in stopped state in order to start pipeline'
                exit(1)


# Check all ELK instances are in a stopped state
opswork = boto.opsworks.connect_to_region(opsworks_region)
check_instance_status(opswork=opswork,
                      opsworks_layer_id=shipper_opsworks_layer_id,
                      layername='Shipper')
check_instance_status(opswork=opswork,
                      opsworks_layer_id=redis_opsworks_layer_id,
                      layername='Redis')
check_instance_status(opswork=opswork,
                      opsworks_layer_id=indexer_opsworks_layer_id,
                      layername='Indexer')

# Check S3 path
s3 = boto.s3.connect_to_region(region, calling_format=OrdinaryCallingFormat())
for item in s3.get_bucket(s3_bucket).list(prefix=path):
    # An object detected inside s3 path
    if item.name != path:
        print 'Detected object ' + item.name + ' . S3 path not empty'
        exit(0)

# No object detected inside s3 path. Returns true to ShellCommand Precondtion
print 'No object detected inside s3 path'
exit(1)
