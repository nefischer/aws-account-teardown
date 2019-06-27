"""Directory Services resources teardown
"""

import time
import boto3


#
# Directory Service
#
def delete_directory_services():
    """Delete all Directory Services

    :return: None
    """
    print('Deleting Directory Services')
    directory_service = boto3.client('ds')
    for directory in directory_service.describe_directories()['DirectoryDescriptions']:
        directory_id = directory['DirectoryId']

        # forwarders are only supported if Type is 'MicrosoftAD'
        if directory['Type'] == 'MicrosoftAD':
            forwarders = directory_service.describe_conditional_forwarders(
                DirectoryId=directory_id
            )['ConditionalForwarders']
            for forwarder in forwarders:
                directory_service.delete_conditional_forwarder(
                    DirectoryId=directory_id,
                    RemoteDomainName=forwarder['RemoteDomainName']
                )
        directory_service.delete_directory(
            DirectoryId=directory['DirectoryId']
        )

    if directory_service.describe_directories()['DirectoryDescriptions']:
        print('Waiting for Directory Services to be destroyed')
        while directory_service.describe_directories()['DirectoryDescriptions']:
            time.sleep(5)
    print('Directory Services deleted')
