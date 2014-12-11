#!/usr/bin/python

# Script for checking if an S3 Path has uploaded objects inside 

region='<aws_region>'
s3_bucket='<s3_bucket>'
path='<path>'
shipper_opsworks_layer_id='<shipper_opsworks_layer_id>'

import boto.opsworks
opswork = boto.opsworks.connect_to_region(region)
for key, value in opswork.describe_instances(layer_id=shipper_opsworks_layer_id).items() :
  for i in range(0,len(value)) :
    shipper_status = value[i].get('Status')
    shipper_opswork_id = value[i].get('InstanceId')
	
    if shipper_status != 'online' :
	  # Shipper should be online in order to do a scaledown
	  exit(1)

import boto.s3
s3 = boto.s3.connect_to_region(region)

for item in s3.get_bucket(s3_bucket).list(prefix=path) :
  # An object detected inside s3 path
  if item.name != path :
    print item.name 
    exit(1)

# No object detected inside s3 path. Returns true to ShellCommand Precondtion 
exit(0)



