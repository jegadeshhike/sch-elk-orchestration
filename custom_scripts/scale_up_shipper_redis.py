#!/usr/bin/python

import time
import boto.opsworks
import os
import argparse

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
parser.add_argument('-e', '--redis_opsworks_layer_id',
                    default='9cd9c603-d417-47e5-8323-65fc086897d4',
                    type=str, help='Opsworks ID of the Redis Layer')
parser.add_argument('-en', '--elk_pipeline_metric_namespace',
                    default='Logstash',
                    type=str,
                    help='Custom Cloudwatch metric namespace used for ' +
                         'ELK Pipeline')
parser.add_argument('-em', '--elk_pipeline_metric_name',
                    default='ELK_Pipeline_Status',
                    type=str,
                    help='Custom Cloudwatch metric name used for ' +
                    'ELK Pipeline')
args = parser.parse_args()
region = args.region
opsworks_region = args.opsworks_region
shipper_opsworks_layer_id = args.shipper_opsworks_layer_id
redis_opsworks_layer_id = args.redis_opsworks_layer_id
elk_pipeline_metric_namespace = args.elk_pipeline_metric_namespace
elk_pipeline_metric_name = args.elk_pipeline_metric_name


def start_instances(opsworks_layer_id, layername):
    print 'Getting status of Opsworks instance(s) in ' + layername + ' Layer'
    opswork = boto.opsworks.connect_to_region(opsworks_region)
    # Get Status of the Opswork instances in Redis layer
    instances_to_monitor = []
    instances = opswork.describe_instances(layer_id=opsworks_layer_id)
    for key, value in instances.items():
        for i in range(0, len(value)):
            status = value[i].get('Status')
            opswork_id = value[i].get('InstanceId')

            if status != 'stopped':
                raise Exception(layername + ' instance with opsworks id ' +
                                opswork_id +
                                ' expected status is stopped.' +
                                ' It is currently ' +
                                status +
                                '. Another process could already be running.')
        # Start instance
        print 'Starting ' + layername + ' instance with opsworks id ' + \
              opswork_id
        opswork.start_instance(opswork_id)
        instances_to_monitor.append(opswork_id)

    # Wait for result. Continually check status of the instance(s)
    while len(instances_to_monitor) > 0:
        instances = opswork.describe_instances(
            instance_ids=instances_to_monitor)
        for key, value in instances.items():
            for i in range(0, len(value)):
                status = value[i].get('Status')
                hostname = value[i].get('Hostname')
                instance_id = value[i].get('InstanceId')
                print ('{0}:Instance  {1} in status {2}').format(time.ctime(),
                                                                 hostname,
                                                                 status)

            # Stop the instances and raise error if at least one of them failed
            if status in ['stopped', 'start_failed', 'setup_failed',
                          'terminating', 'shutting_down', 'terminated']:
                for instance_id in instances_to_monitor:
                    opswork.stop_instance(instance_id)
                raise Exception(layername + ' instance did not come online ' +
                                'successfully. Please check ' +
                                'Opsworks logs for more details. Shutting ' +
                                'it down')
            elif status == 'online':
                instances_to_monitor.remove(instance_id)
        time.sleep(60)


print 'Start time: ' + time.ctime()
# Trigger population custom Cloudwatch metric for the pipeline
os.system("echo '* * * * * /usr/bin/aws cloudwatch put-metric-data " +
          "--metric-name " +
          elk_pipeline_metric_name + " --namespace " +
          elk_pipeline_metric_namespace +
          " --value 1 --region " + region + "' | crontab -")


try:
    start_instances(redis_opsworks_layer_id, 'Redis')
    start_instances(shipper_opsworks_layer_id, 'Shipper')
    print 'Redis and Shipper instances successfully came online.'
except:

    # Flag end of pipeline execution
    os.system("echo '' | crontab -")
    os.system("/usr/bin/aws cloudwatch put-metric-data --metric-name " +
              elk_pipeline_metric_name + " --namespace " +
              elk_pipeline_metric_namespace + " --value=0 --region " + region)
    raise
