import base64
import boto3
import decimal
import time
import urllib.parse


def next_seq(table, tablename):
    response = table.update_item(
        Key={
            'tablename': tablename
        },
        UpdateExpression='set seq = seq + :val',
        ExpressionAttributeValues={
            ':val': 1
        },
        ReturnValues='UPDATED_NEW'
    )

    return response['Attributes']['seq']


def lambda_handler(event, context):
    try:
        dynamodb = boto3.resource('dynamodb')

        seqtable = dynamodb.Table('sequence')
        nextseq = next_seq(seqtable, 'user')

        param = urllib.parse.parse_qs(
            base64.b64decode(event['body']).decode('utf-8'))
        username = param['username'][0]
        email = param['email'][0]

        now = time.time()

        host = event['requestContext']['http']['sourceIp']

        s3 = boto3.client('s3')
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': 'secret-contents-1234',
                'Key': 'secret.jpeg'
            },
            ExpiresIn=48 * 60 * 60,
            HttpMethod='GET'
        )

        usertable = dynamodb.Table('user')
        usertable.put_item(
            Item={
                'id': nextseq,
                'username': username,
                'email': email,
                'accepted_at': decimal.Decimal(str(now)),
                'host': host,
                'url': url
            }
        )

        return {
            'statusCode': 200,
            'headers': {
                'content-type': 'text/html'
            },
            'body': '200'
        }
    except:
        import traceback
        traceback.print_exc()

        return {
            'statusCode': 500,
            'headers': {
                'conetnt-type': 'text/html'
            },
            'body': '500'
        }
