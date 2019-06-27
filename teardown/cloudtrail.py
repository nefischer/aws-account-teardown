"""CloudTrail resources teardown
"""

import time
import boto3


#
# CloudTrail
#
def delete_cloudtrails():
    """Switch off all CloudTrail logs

    :return: None
    """
    client = boto3.client('cloudtrail')
    print('Switching off CloudTrails')
    for trail in client.describe_trails()['trailList']:
        name = trail['Name']
        trail_client = boto3.client('cloudtrail',
                                    region_name=trail['HomeRegion'])
        print('Switching off CloudTrail {}'.format(name))
        trail_client.stop_logging(
            Name=name
        )
        print('Deleting CloudTrail {}'.format(name))
        trail_client.delete_trail(
            Name=name
        )
    while [trail for trail in client.describe_trails()['trailList']]:
        time.sleep(5)
    print('CloudTrail switched off')
