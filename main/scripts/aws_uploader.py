#!usr/bin/env python

'''
Uploads our unicorns JSON file to an Amazon S3 bucket
while keeping a local copy as a backup.
'''

# after pip install boto3 and pip install awscli +
# credentialing on aws with an IAM access key:
import boto3
import re
import datetime


def send_to_s3(filepath):
    '''
    called from pdf_multi_plcb_product_getter.py

    uploads a copy of the file, setting permissions and metadata
    for immediate access

    Args:
    a path to the local JSON file to copy
    '''
    # makes the function more versatile because it doesn't simply rely
    # on today's date to create the s3 filename, ensuring instead it
    # matches whichever of our files gets handed to it
    file_date_pattern = '((?<=\-)\d+.*(?=\.))'
    file_date = re.search(file_date_pattern, filepath).group()
    s3 = boto3.resource('s3')
    f = open(filepath, 'rb')
    k = s3.Bucket('boozicorns').put_object(Key='unicorns-{}.json'.format(file_date),
                                           Body=f,
                                           Metadata={'Content-Type': 'application/json'})
    k.Acl().put(ACL='public-read')
