#!/usr/bin/env python

# Script for checking if an S3 Path has uploaded objects inside

import boto.opsworks
import boto.s3
import argparse
import time

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--region',
                    default='us-west-2',
                    type=str, help='AWS region')
parser.add_argument('-o', '--opsworks_region',
                    default='us-east-1',
                    type=str, help='Opsworks region endpoint')
parser.add_argument('-s', '--shipper_opsworks_layer_id',
                    default='6b51b650-bc78-4bbc-8d0c-67e3b8db22ac',
                    type=str, help='Opsworks ID of the Shipper Layer')
parser.add_argument('-sb', '--source_s3_bucket',
                    default='elkinput-cism-sch',
                    type=str, help='Source S3 bucket for shipper')
parser.add_argument('-sp', '--source_s3_path',
                    default='2-ELK/input/',
                    type=str, help='Path inside source S3 bucket for shipper')
args = parser.parse_args()
region = args.region
opsworks_region = args.opsworks_region
s3_bucket = args.source_s3_bucket
path = args.source_s3_path
if path.endswith('/') is False:
    path = path + '/'
if path.startswith('/') is True:
    path = path[1:]

shipper_opsworks_layer_id = args.shipper_opsworks_layer_id


def s3_prefix_check(s3):
    value = False
    for item in s3.get_bucket(s3_bucket).list(prefix=path):
        # An object detected inside s3 path
        if item.name != path:
            print('Detected object "{}". S3 path not empty'.format(item.name))
            value = True
            break
    return value

# Check status of shipper
opswork = boto.opsworks.connect_to_region(opsworks_region)
instances = opswork.describe_instances(layer_id=shipper_opsworks_layer_id)
for key, value in instances.items():
    for i in range(0, len(value)):
        shipper_status = value[i].get('Status')
        shipper_opswork_id = value[i].get('InstanceId')

        if shipper_status != 'online':
            # Shipper should be online in order to do a scaledown
            print 'Shipper should be online in order to do a scaledown'
            # exit(1)

# Check S3 path
s3 = boto.s3.connect_to_region(region)
value = s3_prefix_check(s3)
while value is True:
    time.sleep(60)
    value = s3_prefix_check(s3)

# No object detected inside s3 path. Returns true to ShellCommand Precondtion
print 'No object detected inside s3 path'
exit(0)
