#!/usr/bin/python

# Script for checking the value of The Logstash Buffer Cloudwatch metric
# Returns true if > 0 for in the last 5 minutes

import boto.ec2.cloudwatch
import datetime
import argparse

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
args = parser.parse_args()
region = args.region
metric_namespace = args.logstash_metric_namespace
metric_name = args.logstash_metric_name


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
        print('Found data point {}. Logstash Buffer is not empty.').format(
            str(value))
        # A normal exit would return true to ShellCommandPrecondition
        exit(0)

# An abnormal exit would return false to ShellCommandPrecondition
print 'Logstash Buffer is empty'
exit(1)
