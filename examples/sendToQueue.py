import json
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('mailaddress')

    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='mail-send-queue-1234')

    for rec in event['Records']:
        backetname = rec['s3']['bucket']['name']
        filename = rec['s3']['object']['key']

        response = table.query(
            IndexName='haserror-index',
            KeyConditionExpression=Key('haserror').eq(0)
        )

        for item in response['Items']:
            email = item['email']
            username = item['username']

            table.update_item(
                Key={'email': email},
                UpdateExpression='set issend=:val',
                ExpressionAttributeValues={
                    ':val': 0
                }
            )

            sqsresponse = queue.send_message(
                MessageBody=email,
                MessageAttributes={
                    'username': {
                        'DataType': 'String',
                        'StringValue': username
                    },
                    'backetname': {
                        'DataType': 'String',
                        'StringValue': backetname
                    },
                    'filename': {
                        'DataType': 'String',
                        'StringValue': filename
                    }
                }
            )

            print(json.dumps(sqsresponse))
