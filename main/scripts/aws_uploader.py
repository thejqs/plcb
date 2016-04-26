#!usr/bin/env python

# after pip install boto3 and pip install awscli +
# credentialing done on aws with an IAM access key:
import boto3
import datetime


def send_to_s3(filepath):
    s3 = boto3.resource('s3')
    f = open(filepath, 'rb')
    k = s3.Bucket('boozicorns').put_object(Key='unicorns-{}.json'.format(datetime.date.today()),
                                           Body=f,
                                           Metadata={'Content-Type': 'application/json'})
    k.Acl().put(ACL='public-read')
