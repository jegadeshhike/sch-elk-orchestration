sch-elk-orchestration
=====================

High-level Description
---------------------
 - Prepares the IAM roles. Sets their permission and trust policies which are defined under iam_policies folder
 - Prepares the custom monitoring scripts and uploads them to S3
 - Drops and rebuilds the Data Pipeline
 - Creates Cloudwatch alarm for each opsworks layer - shipper, redis and indexer

Prerequisites
-------------
 - Parts of the ELK System already in place:
    - Opswork stack created, with shipper, redis and indexer layers
    - Logstash Buffer Custom CloudWatch Metric
    - S3 bucket/path of the logs to be processed by Shipper

 - Prepare the following:
    - SNS Topic ARN used for notification
    - S3 bucket/path created where custom scripts will be stored
    - S3 bucket/path created where DataPipeline will store logs
    - Node with Python boto installed (>=v2.33.0)

Usage
-----
In a node with Python boto installed (>=v2.33.0):

1. Download the code.

         git clone https://github.com/cascadeo/sch-elk-orchestration.git

2. Create an IAM user for ELK. The Data Pipeline objects will be owned by this user. Pipelines aren't visible to other IAM users in the account so a generic IAM user should be used for management. Reference: https://forums.aws.amazon.com/thread.jspa?threadID=138201.

3. Configure IAM user and perform the following:
         - Generate access keys
         - Set its permission policy to iam_policies/iam_user_policy (https://github.com/cascadeo/sch-elk-orchestration/blob/master/iam_policies/iam_user_policy)

	Note: If you wish your own IAM user account to own the pipeline, then ensure your IAM account has the required policies indicated above.

4. Populate deploy_elk_orchestration.cfg configuration file with desired values. Descriptions are placed above the parameters as comments.

5. Run the script.

         python deploy_elk_orchestration.py

6. Log into AWS as the IAM user owner to the AWS Data Pipeline console on the specified region.

7. Make sure all instances in the Opswork stack are stopped. Activate to run the Pipeline.

