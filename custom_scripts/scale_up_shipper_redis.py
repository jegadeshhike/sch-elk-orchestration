#!/usr/bin/python

import time
import boto.opsworks
import os
import argparse

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--region', default='us-east-1',
                    type=str, help='AWS region')
parser.add_argument('-s', '--shipper_opsworks_layer_id',
                    default='9f1f1fa0-6a52-4227-8c54-76dd17873a27',
                    type=str, help='Opsworks ID of the Shipper Layer')
parser.add_argument('-e', '--redis_opsworks_layer_id',
                    default='5175c391-cb2a-49bb-be19-4d588d35d430',
                    type=str, help='Opsworks ID of the Redis Layer')
parser.add_argument('-en', '--elk_pipeline_metric_namespace',
                    default='Pipeline1',
                    type=str,
                    help='Custom Cloudwatch metric namespace used for ' +
                         'ELK Pipeline')
parser.add_argument('-em', '--elk_pipeline_metric_name', default='ELK1',
                    type=str,
                    help='Custom Cloudwatch metric name used for ' +
                    'ELK Pipeline')
args = parser.parse_args()
region = args.region
shipper_opsworks_layer_id = args.shipper_opsworks_layer_id
redis_opsworks_layer_id = args.redis_opsworks_layer_id
elk_pipeline_metric_namespace = args.elk_pipeline_metric_namespace
elk_pipeline_metric_name = args.elk_pipeline_metric_name

print 'Start time: ' + time.ctime()

# Trigger population custom Cloudwatch metric for the pipeline
os.system("echo '* * * * * /usr/bin/aws cloudwatch put-metric-data " +
          "--metric-name " +
          elk_pipeline_metric_name + " --namespace " +
          elk_pipeline_metric_namespace +
          " --value 1 --region " + region + "' | crontab -")

# Get Status of the Opswork instances in Shipper layer
print 'Getting status of Opsworks instances in Shipper and Redis Layers'
opswork = boto.opsworks.connect_to_region(region)
instances_to_monitor = []
instances = opswork.describe_instances(layer_id=shipper_opsworks_layer_id)
for key, value in instances.items():
    for i in range(0, len(value)):
        shipper_status = value[i].get('Status')
        shipper_opswork_id = value[i].get('InstanceId')

    if shipper_status != 'stopped':
        raise Exception('Shipper instance with opsworks id ' +
                        shipper_opswork_id +
                        ' expected status is stopped. It is currently ' +
                        shipper_status +
                        '. Another process could already be running.')

    # Start Shipper instance
    print 'Starting Shipper instance with opsworks id ' + shipper_opswork_id
    opswork.start_instance(shipper_opswork_id)
    instances_to_monitor.append(shipper_opswork_id)

# Get Status of the Opswork instances in Redis layer
instances = opswork.describe_instances(layer_id=redis_opsworks_layer_id)
for key, value in instances.items():
    for i in range(0, len(value)):
        redis_status = value[i].get('Status')
        redis_opswork_id = value[i].get('InstanceId')

        if redis_status != 'stopped':
            raise Exception('Redis instance with opsworks id ' +
                            redis_opswork_id +
                            ' expected status is stopped. It is currently ' +
                            redis_status +
                            '. Another process could already be running.')

    # Start Redis instance
    print 'Starting Redis instance with opsworks id ' + redis_opswork_id
    opswork.start_instance(redis_opswork_id)
    instances_to_monitor.append(redis_opswork_id)

# Wait for result. Continually check status of the Shipper and Redis instances
while len(instances_to_monitor) > 0:
    instances = opswork.describe_instances(instance_ids=instances_to_monitor)
    for key, value in instances.items():
        for i in range(0, len(value)):
            status = value[i].get('Status')
            hostname = value[i].get('Hostname')
            instance_id = value[i].get('InstanceId')
            print ('{}:Instance  {} in status {}').format(time.ctime(),
                                                          hostname,
                                                          status)

        # Stop the instances and raise error if at least one of them failed
        if status in ['stopped', 'start_failed', 'setup_failed',
                      'terminating', 'shutting_down', 'terminated']:
            for instance_id in instances_to_monitor:
                opswork.stop_instance(instance_id)
            raise Exception('One of the shipper and redis instances did ' +
                            'not come online successfully. Please check ' +
                            'Opsworks logs for more details. Shutting ' +
                            'them down')
        elif status == 'online':
            instances_to_monitor.remove(instance_id)

    time.sleep(60)

print 'Shipper and redis instances successfully came online.'
