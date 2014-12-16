#!/usr/bin/python

import time
import boto.opsworks
import argparse

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--region', default='us-east-1',
                    type=str, help='AWS region')
parser.add_argument('-s', '--shipper_opsworks_layer_id', default='9f1f1fa0-6a52-4227-8c54-76dd17873a27',
                    type=str, help='Opsworks ID of the Shipper Layer')
parser.add_argument('-cd', '--cooldown_period', default=3,
                    type=int, help='Cooldown period in minutes before scale down of shipper')
args = parser.parse_args()
region = args.region
shipper_opsworks_layer_id = args.shipper_opsworks_layer_id
cooldown_period_minutes = args.cooldown_period

print 'Start time: ' + time.ctime()

# Wait for cooldown period for drain its buffer
for i in range (0, cooldown_period_minutes) :
  print time.ctime() + ':Waiting for cooldown period before scaling down. ' + \
        str(cooldown_period_minutes-i) + ' minutes left '
  time.sleep(60)

# Get Status of the Opswork instances in Shipper layer
opswork = boto.opsworks.connect_to_region(region)
instances_to_stop=[]
print 'Checking status of Opsworks instances in Shipper Layer'
for key, value in opswork.describe_instances(layer_id=shipper_opsworks_layer_id).items() :
  for i in range(0,len(value)) :
    shipper_status = value[i].get('Status')
    shipper_opswork_id = value[i].get('InstanceId')
	
    if shipper_status != 'online' :
      raise Exception('Shipper instance with opsworks id ' + shipper_opswork_id + \
                      ' expected status is online. It is currently ' + shipper_status + \
                      '. Another process could already be working.')
 
    instances_to_stop.append(shipper_opswork_id)
 
# Stop Shipper instance
for instance in instances_to_stop :
  print 'Stopping Shipper instance with opsworks id ' + instance
  opswork.stop_instance(instance)  

    
