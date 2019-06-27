"""KMS resources teardown
"""

import boto3


#
# KMS Customer Keys
#
def delete_kms_custom_keys():
    """Delete all KMS keys

    :return: None
    """
    client = boto3.client('kms')
    print('Deleting KMS Custom Keys')
    for page in client.get_paginator('list_keys').paginate():
        for key in page['Keys']:
            key_id = key['KeyId']
            metadata = client.describe_key(
                KeyId=key_id
            )['KeyMetadata']
            if metadata['KeyManager'] != 'AWS':
                if metadata['Enabled']:
                    print('Disabling key {}'.format(key_id))
                    client.disable_key(
                        KeyId=key_id
                    )
                if metadata['KeyState'] != 'PendingDeletion':
                    print('Scheduling deletion for key {}'.format(key_id))
                    client.schedule_key_deletion(
                        KeyId=key_id,
                        PendingWindowInDays=7
                    )
    print('KMS Custom Keys deleted')
