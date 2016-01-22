#!/usr/bin/env python

# Script for checking the value of The Logstash Buffer Cloudwatch metric
# Returns true once buffer <= 0 or no data in the last 5 minutes

import boto.opsworks
import boto.ec2.cloudwatch
import datetime
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
parser.add_argument('-ln', '--logstash_metric_namespace',
                    default='Logstash',
                    type=str,
                    help='Custom Cloudwatch metric namespace used for ' +
                    'Logstash Buffer')
parser.add_argument('-lm', '--logstash_metric_name',
                    default='RedisItemsQueued',
                    type=str, help='Custom Cloudwatch metric name used ' +
                    'for Logstash Buffer')
parser.add_argument('-i', '--indexer_opsworks_layer_id',
                    default='be95581a-bbac-457d-84e6-b63a6ca98a9a',
                    type=str, help='Opsworks ID of the Indexer Layer')
args = parser.parse_args()
region = args.region
opsworks_region = args.opsworks_region
metric_namespace = args.logstash_metric_namespace
metric_name = args.logstash_metric_name
indexer_opsworks_layer_id = args.indexer_opsworks_layer_id


def get_cw_metric(cw):
    cw_start_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=300)
    datapoints = cw.get_metric_statistics(period=60,
                                          start_time=cw_start_time,
                                          end_time=datetime.datetime.utcnow(),
                                          namespace=metric_namespace,
                                          metric_name=metric_name,
                                          statistics='Average')
    value = float(datapoints[0].get('Average'))
    return value

# Check status of indexers first
opswork = boto.opsworks.connect_to_region(opsworks_region)
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
value = get_cw_metric(cw)
while value > 0:
    print('Found data point {0}. Logstash Buffer is not empty.').format(
        str(value))
    time.sleep(60)
    value = get_cw_metric(cw)

# A normal exit would return true to ShellCommandPrecondition
print 'Logstash Buffer is empty'
exit(0)
