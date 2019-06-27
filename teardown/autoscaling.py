"""Auto-scaling resources teardown
"""

import time
import boto3


def delete_autoscaling_groups():
    """Delete all auto-scaling groups

    :return: None
    """
    print('Deleting autoscaling groups')
    asg = boto3.client('autoscaling')

    for group in asg.describe_auto_scaling_groups()['AutoScalingGroups']:
        group_name = group['AutoScalingGroupName']
        print('Deleting ASG - {}'.format(group_name))

        asg.delete_auto_scaling_group(
            AutoScalingGroupName=group_name,
            ForceDelete=True
        )

    if asg.describe_auto_scaling_groups()['AutoScalingGroups']:
        print('Waiting for ASG\'s to be destroyed')
        while asg.describe_auto_scaling_groups()['AutoScalingGroups']:
            time.sleep(5)

    print('Autoscaling groups deleted')
