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

    # logger.info(event)

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

        lambdaClient = boto3.client('lambda')
        sns = boto3.client('sns')

        # if eventname == 'CreateFunction':
        if 'CreateFunction' in eventname:
            resourceName=detail['responseElements']['functionArn']
            logger.info(resourceName)

        else:
            logger.info(eventname)
            logger.warning('Not supported action')

        if resourceName:

            logger.info("Delaying 10s before checking tags..")
            time.sleep(10)

            # Get tags
            tags = lambdaClient.list_tags(Resource=resourceName)

            logger.info(tags['Tags'])

            # Check if Creator tag exist
            if 'CreatedBy' not in tags['Tags']:
                logger.info('CreatedBy tag missing, applying tag...')
                lambdaClient.tag_resource(Resource=resourceName, Tags={'CreatedBy': user})
            else:
                logger.info('Creator tag exists, skipping...')

        logger.info(' Remaining time (ms): ' + str(context.get_remaining_time_in_millis()) + '\n')
        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        return False