#!/usr/bin/python

# Script for checking the value of The Logstash Buffer Cloudwatch metric
# Returns true if <= 0 or no data in the last 5 minutes

import boto.opsworks
import boto.ec2.cloudwatch
import datetime
import argparse

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--region', default='us-east-1',
                    type=str, help='AWS region')
parser.add_argument('-ln', '--logstash_metric_namespace', default='Logstash',
                    type=str,
                    help='Custom Cloudwatch metric namespace used for ' +
                         'Logstash Buffer')
parser.add_argument('-lm', '--logstash_metric_name',
                    default='RedisItemsQueued',
                    type=str, help='Custom Cloudwatch metric name used ' +
                                   'for Logstash Buffer')
parser.add_argument('-i', '--indexer_opsworks_layer_id',
                    default='9cafbed2-a248-40a4-8b9d-0a68a8629771',
                    type=str, help='Opsworks ID of the Indexer Layer')
args = parser.parse_args()
region = args.region
metric_namespace = args.logstash_metric_namespace
metric_name = args.logstash_metric_name
indexer_opsworks_layer_id = args.indexer_opsworks_layer_id


# Check status of indexers first
opswork = boto.opsworks.connect_to_region(region)
instances = opswork.describe_instances(layer_id=indexer_opsworks_layer_id)
for key, value in instances.items():
    for i in range(0, len(value)):
        indexer_status = value[i].get('Status')
        indexer_opswork_id = value[i].get('InstanceId')

        if indexer_status != 'online':
            # Indexers should be online in order to do a scaledown
            print 'Indexers should be online in order to do a scaledown'
            exit(1)

# Check Logstash Buffer
cw = boto.ec2.cloudwatch.connect_to_region(region)
cw_start_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=300)
datapoints = cw.get_metric_statistics(period=60,
                                      start_time=cw_start_time,
                                      end_time=datetime.datetime.utcnow(),
                                      namespace=metric_namespace,
                                      metric_name=metric_name,
                                      statistics='Average')

for dp in datapoints:
    value = float(dp.get('Average'))
    if value > 0:
        print ('Found datapoint {}. Logstash Buffer is not empty.').format(
            str(value))
    # An abnormal exit would return false to ShellCommandPrecondition
    exit(1)

# A normal exit would return true to ShellCommandPrecondition
print 'Logstash Buffer is empty'
exit(0)
