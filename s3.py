from __future__ import print_function
import json
import boto3
import logging
import time
import datetime
import urllib2
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    resourceName = ''

    try:
        region = event['region']
        detail = event['detail']
        eventname = detail['eventName']
        arn = detail['userIdentity']['arn']
        principal = detail['userIdentity']['principalId']
        userType = detail['userIdentity']['type']

        if userType == 'IAMUser':
            user = detail['userIdentity']['userName']
        elif userType == 'Root':
            user = detail['userIdentity']['userName']
        else:
            try:
                user = principal.split(':')[1]
            except:
                user = accountNumber

        if not detail['requestParameters']:
            logger.warning('Not requestParameters found')
            if detail['errorCode']:
                logger.error('errorCode: ' + detail['errorCode'])
            if detail['errorMessage']:
                logger.error('errorMessage: ' + detail['errorMessage'])
            return False

        s3 = boto3.client('s3')
        sns = boto3.client('sns')

        if eventname == 'CreateBucket':
            resourceName=detail['requestParameters']['bucketName']
            logger.info(resourceName)

        else:
            logger.warning('Not supported action')

        if resourceName:
            logger.info("Delaying 5s before checking tags..")
            time.sleep(5)
            print('Tagging resource ' + resourceName)
            s3.put_bucket_tagging(Bucket=resourceName, Tagging={'TagSet':[{'Key': 'CreatedBy', 'Value': user}]})

        logger.info(' Remaining time (ms): ' + str(context.get_remaining_time_in_millis()) + '\n')
        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        return False