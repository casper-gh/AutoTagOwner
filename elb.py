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

    resourceNames = []

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

        elb = boto3.client('elb')
        sns = boto3.client('sns')

        if eventname == 'CreateLoadBalancer':
            resourceNames.append(detail['requestParameters']['loadBalancerName'])
            logger.info(resourceNames)

        else:
            logger.warning('Not supported action')

        if resourceNames:
            count = 0
            for resourceid in resourceNames:
                logger.info("Delaying 3s before checking tags..")
                time.sleep(3)
                tags = elb.describe_tags(LoadBalancerNames=[resourceid])
                tag_names = set(subd.get('Key') for subd in tags['TagDescriptions'][count]['Tags'])
                # Apply creator tag if none is found
                creatorTagFound = all(tag in tag_names for tag in ('Creator'))
                if not creatorTagFound:
                    logger.info('Creator tag missing, applying tag...')
                    elb.add_tags(LoadBalancerNames=resourceNames, Tags=[{'Key': 'CreatedBy', 'Value': user}])

        logger.info(' Remaining time (ms): ' + str(context.get_remaining_time_in_millis()) + '\n')
        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        return False