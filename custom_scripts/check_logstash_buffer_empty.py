#!/usr/bin/python

# Script for checking the value of The Logstash Buffer Cloudwatch metric
# Returns true if <= 0 or no data in the last 5 minutes

region='<aws_region>'
metric_namespace='<metric_namespace>'
metric_name='<metric_name>'
indexer_opsworks_layer_id='<indexer_opsworks_layer_id>'

import boto.opsworks
opswork = boto.opsworks.connect_to_region(region)
for key, value in opswork.describe_instances(layer_id=indexer_opsworks_layer_id).items() :
  for i in range(0,len(value)) :
    indexer_status = value[i].get('Status')
    indexer_opswork_id = value[i].get('InstanceId')

    if indexer_status != 'online' :
      # Indexers should be online in order to do a scaledown
      print 'Indexers should be online in order to do a scaledown'
      exit(1)

import boto.ec2.cloudwatch
import datetime
cw = boto.ec2.cloudwatch.connect_to_region(region)

datapoints = cw.get_metric_statistics(period=60,start_time=(datetime.datetime.utcnow() - datetime.timedelta(seconds=300)), end_time=datetime.datetime.utcnow(), namespace=metric_namespace, metric_name=metric_name, statistics='Average')

for dp in datapoints :
  value = float(dp.get('Average'))
  if value > 0 :
    print value
    # An abnormal exit would return false to ShellCommandPrecondition
    exit(1)

# A normal exit would return true to ShellCommandPrecondition
print 'Here'
exit(0)
