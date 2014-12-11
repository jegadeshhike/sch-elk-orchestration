sch-elk-orchestration
=====================

Instructions:

1. Create an IAM user for ELK. The Data Pipeline objects will be owned by this user. Pipelines aren't visible to other IAM users in the account so a generic IAM user should be used for management.

         https://forums.aws.amazon.com/thread.jspa?threadID=138201

2. Configure IAM User.
         - Genearte access keys
         - Set its permission policy to iam_policies/iam_user_policy

3. Python Boto at least v2.33.0 is needed to run. One can use the latest Amazon AMI Linux provided by AWS.

4. Download the code

         https://github.com/roy-cascadeo/sch-elk-orchestration.git

5. Populate configuration cfg file with correct values

         - General Settings section
                - access keys of the created IAM user
                - aws region - all objects are expected to be created under this region
         - Opsworks Settings section
                - indicate the opsworks id of the shipper, redis and indexer layers 
         - Custom Script Settings section 
                - the s3 bucket and path to upload the custom script. Bucket is expected to be in the same region .
                - s3 bucket location and path of the firewall logs processes by shipper
                - some cooldown period
         - Cloudwatch Settings section
                - details of the Logstash buffer metric
                - period to evaluation for cloudwatch alarms to be created for overrunning cases
                - arn of SNS topic to alert
         - Data Pipeline Settings section
                - Data Pipelien IAM roles
                    - pipeline_role - used by service
                    - pipeline_resource_role - the instance profile used by the instances launched by the service
                - Each Pipeline object is represented by a parameter with dictionary definitions. Update their fields to desired values

6. Run the script

       python deploy_elk_orchestration.py

   High Level on What the script does
       - Prepares the IAM roles. Sets their permission and trust policies which are defined under iam_policies folder
       - Prepares the custom monitoring scripts and uploads them to S3
       - Drops and rebuilds the Data Pipeline
       - Creates Clodwatch alarm for each opsworks layer - shipper, redis and indexer 

7. Log on as your IAM USer to the AWS Data Pipeline console on the specified region.

8. Activate to run the Pipeline

