#!usr/bin/env python

'''
Uploads our unicorns JSON file to an Amazon S3 bucket
while keeping a local copy as a backup.

The regex, rather than the earlier use of datetime, makes it easier
to use this on a batch of files the way filenames are structured
for this project. At some point I'm probably going to need to also run this
to restore broken data or populate a new bucket. I mean, Let's be real.

For example, could be used on a full directory as a module:
import os
import re
import boto3
from aws_uploader import send_to_s3

for fp in os.listdir('../data/unicorns_json'):
    send_to_s3('../data/unicorns_json/' + fp)

'''

# after pip install boto3 and pip install awscli +
# credentialing on aws with `aws configure` and an IAM user access key:
import boto3
import re

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
    # matches whichever of our files gets handed to it.
    # this makes it easier to run while looping through a directory.
    file_date_pattern = '((?<=\-)\d+.*(?=\.))'
    file_date = re.search(file_date_pattern, filepath).group()
    s3 = boto3.resource('s3')
    f = open(filepath, 'rb')
    k = s3.Bucket('boozicorns').put_object(Key='unicorns-{}.json'.format(file_date),
                                           Body=f,
                                           Metadata={'Content-Type': 'application/json'})
    k.Acl().put(ACL='public-read')
