"""Kinesis resources teardown
"""

import time
import boto3


#
# Kinesis data streams
#
def delete_kinesis_data_streams():
    """Delete all Kinesis data streams

    :return: None
    """
    client = boto3.client('kinesis')
    print('Deleting Kinesis Streams')
    for page in client.get_paginator('list_streams').paginate():
        for stream_name in page['StreamNames']:
            print('Deleting Kinesis Stream {}'.format(stream_name))
            client.delete_stream(
                StreamName=stream_name
            )
            time.sleep(0.25)
    print('Kinesis Streams deleted')


#
# Kinesis applications
#
def delete_kinesis_applications():
    """Delete all Kinesis applications

    :return: None
    """
    client = boto3.client('kinesisanalytics')
    print('Deleting Kinesis Applications')
    list_applications_resp = client.list_applications()
    start_from_app = None
    while True:
        for application_summary in list_applications_resp['ApplicationSummaries']:
            name = application_summary['ApplicationName']
            print('Deleting Kinesis Application {}'.format(name))
            app_detail = client.describe_application(
                ApplicationName=name
            )['ApplicationDetail']
            client.delete_application(
                ApplicationName=name,
                CreateTimestamp=app_detail['CreateTimestamp']
            )
            start_from_app = name
        if list_applications_resp['HasMoreApplications'] and start_from_app:
            list_applications_resp = client.list_applications(
                ExclusiveStartApplicationName=start_from_app
            )
        else:
            break
    while client.list_applications()['ApplicationSummaries']:
        time.sleep(5)
    print('Kinesis Applications deleted')
