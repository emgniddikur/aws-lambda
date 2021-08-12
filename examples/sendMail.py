import boto3

sqs = boto3.resource('sqs')

s3 = boto3.resource('s3')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('mailaddress')

client = boto3.client('ses', region_name='us-east-1')
MAILFROM = 'yoshiharu2580@gmail.com'


def lambda_handler(event, context):
    for rec in event['Records']:
        snsmessage = rec['Sns']['Message']
        queue = sqs.get_queue_by_name(QueueName=snsmessage)
        messages = queue.receive_messages(
            MessageAttributeNames=['All'],
            MaxNumberOfMessages=10
        )
        for m in messages:
            if m.message_attributes is not None:
                print('Sending...')

                email = m.body
                username = m.message_attributes.get(
                    'username').get('StringValue')
                backetname = m.message_attributes.get(
                    'backetname').get('StringValue')
                filename = m.message_attributes.get(
                    'filename').get('StringValue')

                print(email)
                print(username)
                print(backetname)
                print(filename)

                obj = s3.Object(backetname, filename)
                response = obj.get()
                maildata = response['Body'].read().decode('utf-8')
                data = maildata.split('\n', 3)
                subject = data[0]
                body = data[2]

                print(subject)
                print(body)

                response = table.update_item(
                    Key={
                        'email': email
                    },
                    UpdateExpression='set issend=:val',
                    ExpressionAttributeValues={
                        ':val': 1
                    },
                    ReturnValues='UPDATED_OLD'
                )

                if response['Attributes']['issend'] == 0:
                    response = client.send_email(
                        Source=MAILFROM,
                        ReplyToAddresses=[MAILFROM],
                        Destination={
                            'ToAddresses': [email]
                        },
                        Message={
                            'Subject': {
                                'Data': subject,
                                'Charset': 'UTF-8'
                            },
                            'Body': {
                                'Text': {
                                    'Data': body,
                                    'Charset': 'UTF-8'
                                }
                            }
                        }
                    )
                else:
                    print('Resend Skip')

                print("Send To" + email)
            else:
                print("Message None")

            m.delete()
