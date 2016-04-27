#!usr/bin/env python

'''
Uploads our unicorns JSON file to an Amazon S3 bucket
while keeping a local copy as a backup.
'''

# after pip install boto3 and pip install awscli +
# credentialing on aws with an IAM access key:
import boto3
import datetime


def send_to_s3(filepath):
    '''
    called from pdf_multi_plcb_product_getter.py

    uploads a copy of the file, setting permissions and metadata
    for immediate access

    Args:
    a path to the local JSON file to copy
    '''
    s3 = boto3.resource('s3')
    f = open(filepath, 'rb')
    k = s3.Bucket('boozicorns').put_object(Key='unicorns-{}.json'.format(datetime.date.today()),
                                           Body=f,
                                           Metadata={'Content-Type': 'application/json'})
    k.Acl().put(ACL='public-read')
