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

    ids = []

    logger.info("Begin loading event")
    logger.info("Delaying 10s before running scripts..")
    time.sleep(30)
    try:
        region = event['region']
        detail = event['detail']
        eventname = detail['eventName']
        arn = detail['userIdentity']['arn']
        principal = detail['userIdentity']['principalId']
        userType = detail['userIdentity']['type']

        # Check if instance is launched by ASG
        isASG = False;
        try:
            invokedBy = detail['userIdentity']['invokedBy']
            if invokedBy == 'autoscaling.amazonaws.com':
                isASG = True
        except:
            isASG = False

        # Delay for 3 min
        if isASG == True:
            logger.info("Instance is launched by ASG, waiting for 3 mins before checking tags...")
            time.sleep(200)

        if userType == 'IAMUser':
            user = detail['userIdentity']['userName']
        elif userType == 'Root':
            user = detail['userIdentity']['userName']
        else:
            try:
                user = principal.split(':')[1]
            except:
                user = accountNumber

        logger.info("Successfully loaded event message")
        if not detail['responseElements']:
            logger.warning('Not responseElements found')
            if detail['errorCode']:
                logger.error('errorCode: ' + detail['errorCode'])
            if detail['errorMessage']:
                logger.error('errorMessage: ' + detail['errorMessage'])
            return False

        ec2 = boto3.client('ec2')
        sns = boto3.client('sns')

        logger.info("Getting info from RunInstances event")
        if eventname == 'RunInstances':
            items = detail['responseElements']['instancesSet']['items']
            for item in items:
                ids.append(item['instanceId'])
            logger.info(ids)
            logger.info('number of instances: ' + str(len(ids)))
        else:
            logger.warning('Not supported action')

        if ids:
            logger.info("Begin looping thru each EC2 resource")
            for resourceid in ids:
                logger.info("Delaying 3s before checking tags..")
                time.sleep(3)
                print('Tagging resource ' + resourceid)
                tags = ec2.describe_tags(
                    Filters=[
                        {
                            'Name': 'resource-id',
                            'Values': [
                                resourceid,
                            ]
                        },
                    ],
                )
                # Apply creator tag if none is found
                tag_names = ''
                tag_names = set(subd.get('Key') for subd in tags['Tags'])
                try:
                    creatorTagFound = all(tag in tag_names for tag in ('Creator'))
                    if not creatorTagFound:
                        logger.info('Creator tag missing, applying tag...')
                        ec2.create_tags(Resources=ids, Tags=[{'Key': 'CreatedBy', 'Value': user}])
                except:
                    logger.info('No tag found at all, applying tag...')
                    ec2.create_tags(Resources=ids, Tags=[{'Key': 'CreatedBy', 'Value': user}])

        logger.info(' Remaining time (ms): ' + str(context.get_remaining_time_in_millis()) + '\n')
        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        return False