#!/usr/bin/python

region='<aws_region>'
shipper_opsworks_layer_id='<shipper_opsworks_layer_id>'
redis_opsworks_layer_id='<redis_opsworks_layer_id>'

import time
import boto.opsworks
print 'Start time: ' + time.ctime()
print 'Getting status of Opsworks instances in Shipper and Redis Layers'
opswork = boto.opsworks.connect_to_region(region)
instances_to_monitor=[]

# Get Status of the Opswork instances in Shipper layer
for key, value in opswork.describe_instances(layer_id=shipper_opsworks_layer_id).items() :
  for i in range(0,len(value)) :
    shipper_status = value[i].get('Status')
    shipper_opswork_id = value[i].get('InstanceId')
	
    if shipper_status != 'stopped' :
      raise Exception('Shipper instance with opsworks id ' + shipper_opswork_id + ' expected status is stopped. It is currently ' + shipper_status + '. Another process could already be running.')
 
    # Start Shipper instance
    print 'Starting Shipper instance with opsworks id ' + shipper_opswork_id
    opswork.start_instance(shipper_opswork_id) 
    instances_to_monitor.append(shipper_opswork_id)
 
 
# Get Status of the Opswork instances in Redis layer
for key, value in opswork.describe_instances(layer_id=redis_opsworks_layer_id).items() :
  for i in range(0,len(value)) :
    redis_status = value[i].get('Status')
    redis_opswork_id = value[i].get('InstanceId')
  
    if redis_status != 'stopped' :
      raise Exception('Redis instance with opsworks id ' + redis_opswork_id + ' expected status is stopped. It is currently ' + redis_status + '. Another process could already be running.')
 
    # Start Redis instance
    print 'Starting Redis instance with opsworks id ' + redis_opswork_id
    opswork.start_instance(redis_opswork_id) 
    instances_to_monitor.append(redis_opswork_id)
  
# Wait for result. Continually check status of the Shipper and Redis instances
while len(instances_to_monitor) > 0 :
  for key, value in opswork.describe_instances(instance_ids=instances_to_monitor).items() :
    for i in range(0,len(value)) :
	  status = value[i].get('Status')
	  hostname =value[i].get('Hostname')
	  instance_id = value[i].get('InstanceId')
	  print time.ctime() + ':Instance  '+ hostname + ' in ' + status + ' status.'
		
	  # Stop the instances and raise error if at least one of them failed 
	  if status in ['stopped', 'start_failed', 'setup_failed', 'terminating', 'shutting_down', 'terminated'] :	  
	    for instance_id in instances_to_monitor :
		  opswork.stop_instance(instance_id)
	    raise Exception( 'One of the shipper and redis instances did not come online successfully. Please check Opsworks logs for more details. Shutting them down')
	  elif status == 'online' :
	    instances_to_monitor.remove(instance_id) 
		
  time.sleep(60)
  
print 'Shipper and redis instances successfully came online.'
    
