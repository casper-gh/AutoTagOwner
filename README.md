# AutoTagOwner
Automatically create `CreatedBy` tag for resources on launched based on IAM usernames.

*Supported resources:*
- EC2
- DynamoDB
- Elastic Load Balancer
- ElasticSearch
- Lambda
- RDS
- S3

You are welcome to add support for other resources.

***Usage:***

1. Enable Cloudtrail logs for current AWS account.
2. Create an S3 bucket to keep all lambda function codes.
3. Create individual zip for each python function. For example: ec2.py --> ec2.zip.
4. Upload all .zip files to S3 bucket.
5. Deloy this Cloudformation template, use S3 bucket name created above for template parameter.
6. Test!

**Note:**

This CF template deloys resource tagging for all of the services listed above. So if you only need to auto tag 1 or fewer services, remove them from the template. Take a look at the AutoTagEC2.json for example (upload only ec2.zip to S3).

