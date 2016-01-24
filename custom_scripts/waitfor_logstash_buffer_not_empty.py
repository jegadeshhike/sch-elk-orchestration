#!/usr/bin/env python

# Script for checking the value of the Logstash buffer Cloudwatch metric
# Returns true once buffer metric > 0 in the last 5 minutes

import boto.ec2.cloudwatch
import datetime
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--region',
                    default='us-west-2',
                    type=str, help='AWS region')
parser.add_argument('-ln', '--logstash_metric_namespace',
                    default='Logstash',
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


def get_cw_metric(cw):
    cw_start_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=300)
    datapoints = cw.get_metric_statistics(period=60,
                                          start_time=cw_start_time,
                                          end_time=datetime.datetime.utcnow(),
                                          namespace=metric_namespace,
                                          metric_name=metric_name,
                                          statistics='Average')
    # print('datapoints: {}'.format(datapoints))
    # print('datapoints[0]: {}'.format(datapoints[0]))
    value = float(datapoints[0].get('Average'))
    # print('value: {}'.format(value))
    return value

cw = boto.ec2.cloudwatch.connect_to_region(region)
value = get_cw_metric(cw)
while value == 0:
    print('Found data point {0}. Logstash Buffer is empty.').format(
        str(value))
    time.sleep(60)
    value = get_cw_metric(cw)

# An abnormal exit would return false to ShellCommand
print 'Logstash Buffer is not empty'
exit(0)
