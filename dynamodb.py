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

        if not detail['responseElements']:
            logger.warning('Not responseElements found')
            if detail['errorCode']:
                logger.error('errorCode: ' + detail['errorCode'])
            if detail['errorMessage']:
                logger.error('errorMessage: ' + detail['errorMessage'])
            return False

        dynamodb = boto3.client('dynamodb')
        sns = boto3.client('sns')

        if eventname == 'CreateTable':
            resourceName=detail['responseElements']['tableDescription']['tableArn']
            logger.info(resourceName)

        else:
            logger.warning('Not supported action')

        if resourceName:
            time.sleep(10)
            tags = dynamodb.list_tags_of_resource(ResourceArn=resourceName)
            tag_names = set(subd.get('Key') for subd in tags['Tags'])
            # Billing tags
            tagFound = all(tag in tag_names for tag in ('CreatedBy'))
            if not tagFound:
                logger.info('Tag missing, applying createdBy...')
                dynamodb.tag_resource(ResourceArn=resourceName, Tags=[{'Key': 'CreatedBy', 'Value': user}])
            else:
                logger.info('Tag found, exiting...')

        logger.info(' Remaining time (ms): ' + str(context.get_remaining_time_in_millis()) + '\n')
        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        return False