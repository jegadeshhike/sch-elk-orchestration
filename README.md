[![Build Status](https://secure.travis-ci.org/SCH-CISM/sch-elk-orchestration.png)](http://travis-ci.org/SCH-CISM/sch-elk-orchestration)

sch-elk-orchestration
=====================

High-level Description
---------------------
 - Prepares the IAM roles; sets their permission and trust policies as defined in the iam_policies folder
 - Prepares the custom monitoring scripts and uploads them to S3
 - Prepares the Chef cookbooks for use in OpsWorks
 - Creates the OpsWorks stack
 - Creates the Data Pipeline for scheduled batch uploads
 - Creates Cloudwatch alarm for the ELK Pipeline

Prerequisites
-------------
 - AWSCLI installed and configured
 - Git installed and configured
 - Chef-DK installed and configured

 - Parts of the ELK System already in place:
    - Logstash Buffer Custom CloudWatch Metric
    - S3 bucket/path of the logs to be processed by Shipper

 - Prepare the following:
    - SNS Topic ARN used for notification
    - S3 bucket/path created where custom scripts will be stored
    - S3 bucket/path created where DataPipeline will store logs

Usage
-----

1. Download the code.

`git clone https://github.com/SCH-CISM/sch-elk-orchestration.git`

2. Prepare the Chef cookbooks

`cd .\cookbooks; berks package elk-cookbooks.tar.gz; cd ..`

3. Upload the Chef cookbooks to s3

`aws s3 cp .\cookbooks\elk-cookbooks.tar.gz s3://YOUBUCKET/cookbooks/ --sse`

2. Upload the contents of `custom_scripts` to the `bin` directory of your 
infrastructure bucket.

`aws s3 cp .\custom_scripts\ s3://YOURBUCKET/bin --recursive --sse`

3. Upload the cloudformation templates to the `cloudformation` directory of your 
infrastructure bucket.

`aws s3 cp .\cloudformation\ s3://YOURBUCKET/cloudformation --recursive --sse`

4. Create the IAM roles

`aws cloudformation --stack-name STACKNAME --template-url https://s3-us-west-2.amazonaws.com/YOUBUCKET/cloudformation/elk-iam-roles.json --parmaeters ParameterKey=MaxMindLicenseKey,ParameterValue=YOURKEYSTRING`

5. Create the ELK OpsWorks stack

`aws cloudformation --stack-name STACKNAME --template-url https://s3-us-west-2.amazonaws.com/YOUBUCKET/cloudformation/elk-opsworks-stack.json --parmaeters ParameterKey=MaxMindLicenseKey,ParameterValue=YOURKEYSTRING`

6. Get the layer IDs for the newly created stack

`aws opsworks describe-layers --stack-id STACKID --region us-east-1 | C:\localbin\jq.exe ".Layers[] | {LayerId, Name}"`

7. Launch the instances in the ES and KB layers

8. Create the ELK pipeline

`aws cloudformation --stack-name STACKNAME --template-url https://s3-us-west-2.amazonaws.com/YOUBUCKET/cloudformation/elk-opsworks-stack.json --parmaeters ParameterKey=OpsworksShipperLayerID,ParameterValue=LSLAYERID,ParameterKey=OpsworksIndexerLayerID,ParameterValue=LSIXLAYERID,ParameterKey=OpsworksRedisLayerID,ParameterValue=RSLAYERID`