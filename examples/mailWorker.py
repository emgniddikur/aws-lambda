import boto3

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='mail-send-queue-1234')

sns = boto3.resource('sns')
topic = sns.Topic(
    'arn:aws:sns:ap-northeast-1:075761447707:sendmail-notifications')


def lambda_handler(event, context):
    n = queue.attributes['ApproximateNumberOfMessages']
    for _ in range(int((int(n) + 9) / 10)):
        topic.publish(
            Message='mail-send-queue-1234'
        )
