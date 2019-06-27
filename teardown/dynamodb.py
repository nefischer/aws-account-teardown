"""DynamoDB resources teardown
"""

import time
import boto3


#
# DynamoDB
#
def delete_dynamodb_instances():
    """Delete all DynamoDB instances

    :return: None
    """
    print('Deleting DynamoDB tables')
    client = boto3.client('dynamodb')
    for page in client.get_paginator('list_tables').paginate():
        for table in page['TableNames']:
            print('Deleting DynamoDB table {}'.format(table))
            client.delete_table(
                TableName=table
            )
    while client.list_tables()['TableNames']:
        time.sleep(5)
    print('DynamoDB tables deleted')

    print('Deleting DynamoDB backups')
    for page in client.get_paginator('list_backups').paginate():
        for backup in page['BackupSummaries']:
            backup_arn = backup['BackupArn']
            print('Deleting DynamoDB backup {}'.format(backup_arn))
            client.delete_backup(
                BackupArn=backup_arn
            )
    while client.list_backups()['BackupSummaries']:
        time.sleep(5)
    print('DynamoDB backups deleted')
