"""SSM resources teardown
"""

import boto3


#
# SSM Parameters
#
def delete_ssm_parameters():
    """Delete all SSM parameters

    :return: None
    """
    client = boto3.client('ssm')
    print('Deleting SSM Parameters')
    for page in client.get_paginator('describe_parameters').paginate():
        for param in page['Parameters']:
            name = param['Name']
            print('Deleting SSM Parameter {}'.format(name))
            client.delete_parameter(
                Name=name
            )
    print('SSM Parameters deleted')
