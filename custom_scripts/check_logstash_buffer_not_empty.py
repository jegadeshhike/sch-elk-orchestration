#!/usr/bin/python

# Script for checking the value of The Logstash Buffer Cloudwatch metric
# Returns true if > 0 for in the last 5 minutes

region='<aws_region>'
metric_namespace='<metric_namespace>'
metric_name='<metric_name>'

import boto.ec2.cloudwatch
import datetime
cw = boto.ec2.cloudwatch.connect_to_region(region)

datapoints = cw.get_metric_statistics(period=60,start_time=(datetime.datetime.utcnow() - datetime.timedelta(seconds=300)), end_time=datetime.datetime.utcnow(), namespace=metric_namespace, metric_name=metric_name, statistics='Average')

for dp in datapoints :
  value = float(dp.get('Average'))
  if value > 0 :
    print value
    # A normal exit would return true to ShellCommandPrecondition
    exit(0)

# An abnormal exit would return false to ShellCommandPrecondition
exit(1)
