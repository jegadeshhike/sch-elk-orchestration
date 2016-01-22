#!/usr/bin/python

import time
import boto.opsworks
import argparse
import os

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--region',
                    default='us-west-2',
                    type=str, help='AWS region')
parser.add_argument('-o', '--opsworks_region',
                    default='us-east-1',
                    type=str, help='Opsworks region endpoint')
parser.add_argument('-i', '--indexer_opsworks_layer_id',
                    default='be95581a-bbac-457d-84e6-b63a6ca98a9a',
                    type=str, help='Opsworks ID of the Indexer Layer')
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
indexer_opsworks_layer_id = args.indexer_opsworks_layer_id
elk_pipeline_metric_name = args.elk_pipeline_metric_name
elk_pipeline_metric_namespace = args.elk_pipeline_metric_namespace

print 'Start time: ' + time.ctime()
# Trigger population custom Cloudwatch metric for the pipeline
os.system("echo '* * * * * /usr/bin/aws cloudwatch put-metric-data " +
          "--metric-name " +
          elk_pipeline_metric_name + " --namespace " +
          elk_pipeline_metric_namespace +
          " --value 1 --region " + region + "' | crontab -")

try:
    # Get Status of the Opswork instances in Indexer layer
    print 'Getting status of Opsworks instances in Indexer Layer'
    opswork = boto.opsworks.connect_to_region(opsworks_region)
    instances_to_monitor = []
    instances = opswork.describe_instances(layer_id=indexer_opsworks_layer_id)
    for key, value in instances.items():
        for i in range(0, len(value)):
            indexer_status = value[i].get('Status')
            indexer_opswork_id = value[i].get('InstanceId')

            if indexer_status != 'stopped':
                raise Exception('Indexer instance with opsworks id ' +
                                indexer_opswork_id +
                                ' expected status is stopped. ' +
                                'It is currently ' + indexer_status +
                                '. Another process could already be running.')

            # Start Indexer instance
            print 'Starting Indexer instance with opsworks id ' + \
                  indexer_opswork_id
            opswork.start_instance(indexer_opswork_id)
            instances_to_monitor.append(indexer_opswork_id)

    # Wait for result. Continually check status of the instances
    while len(instances_to_monitor) > 0:
        instances = opswork.describe_instances(
            instance_ids=instances_to_monitor)
        for key, value in instances.items():
            for i in range(0, len(value)):
                status = value[i].get('Status')
                hostname = value[i].get('Hostname')
                instance_id = value[i].get('InstanceId')
                print('{0}:Instance  {1}' +
                      ' in {2} status.').format(time.ctime(),
                                                hostname, status)

                # Stop the instances and
                # raise error if at least one of them failed
                if status in ['stopped', 'start_failed', 'setup_failed',
                              'terminating', 'shutting_down', 'terminated']:
                    for instance_id in instances_to_monitor:
                        opswork.stop_instance(instance_id)
                        raise Exception('One of the indexer instances did ' +
                                        'not come online successfully. ' +
                                        'Please check Opsworks logs for ' +
                                        'more details. Shutting them down')
                elif status == 'online':
                    instances_to_monitor.remove(instance_id)

        time.sleep(60)

    print 'Indexer instances successfully came online.'
except:
    # Flag end of pipeline execution
    os.system("echo '' | crontab -")
    os.system("/usr/bin/aws cloudwatch put-metric-data --metric-name " +
              elk_pipeline_metric_name + " --namespace " +
              elk_pipeline_metric_namespace + " --value=0 --region " + region)
    raise
