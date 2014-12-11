#!/usr/bin/python

region='<aws_region>'
indexer_opsworks_layer_id='<indexer_opsworks_layer_id>'

import time
import boto.opsworks
print 'Start time: ' + time.ctime()
print 'Getting status of Opsworks instances in Indexer Layer'
opswork = boto.opsworks.connect_to_region(region)
instances_to_monitor=[]

# Get Status of the Opswork instances in Indexer layer
for key, value in opswork.describe_instances(layer_id=indexer_opsworks_layer_id).items() :
  for i in range(0,len(value)) :
    indexer_status = value[i].get('Status')
    indexer_opswork_id = value[i].get('InstanceId')
	
    if indexer_status != 'stopped' :
      raise Exception('Indexer instance with opsworks id ' + indexer_opswork_id + ' expected status is stopped. It is currently ' + indexer_status + '. Another process could already be running.')
 
    # Start Indexer instance
    print 'Starting Indexer instance with opsworks id ' + indexer_opswork_id
    opswork.start_instance(indexer_opswork_id) 
    instances_to_monitor.append(indexer_opswork_id)
 
  
# Wait for result. Continually check status of the instances
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
	    raise Exception( 'One of the indexer instances did not come online successfully. Please check Opsworks logs for more details. Shutting them down')
	  elif status == 'online' :
	    instances_to_monitor.remove(instance_id) 
		
  time.sleep(60)
  
print 'Indexer instances successfully came online.'
    
