"""ELB resources teardown
"""

import time
import boto3


def delete_classic_load_balancers():
    """Delete all the classic Elastic Load Balancers

    :return: None
    """
    print('Deleting classic load balancers')
    elb = boto3.client('elb')

    for load_balancer in elb.describe_load_balancers()['LoadBalancerDescriptions']:
        lb_name = load_balancer['LoadBalancerName']
        print('Deleting LB - {}'.format(lb_name))

        elb.delete_load_balancer(
            LoadBalancerName=lb_name
        )

    while [lb for lb in elb.describe_load_balancers()['LoadBalancerDescriptions']]:
        time.sleep(5)

    print('Classic load balancers deleted')


#
# ELBv2
#
def delete_load_balancers_v2():
    """Delete all new Load Balancer types (application and network)

    :return: None
    """
    print('Deleting Load Balancers v2')
    elbv2 = boto3.client('elbv2')

    for load_balancer in elbv2.describe_load_balancers()['LoadBalancers']:
        lb_arn = load_balancer['LoadBalancerArn']
        print('Deleting LB v2 - {}'.format(lb_arn))

        elbv2.delete_load_balancer(
            LoadBalancerArn=lb_arn
        )

    if elbv2.describe_load_balancers()['LoadBalancers']:
        print('Waiting for LB v2 to be destroyed')
        while elbv2.describe_load_balancers()['LoadBalancers']:
            time.sleep(5)
    print('Load Balancers v2 deleted')


#
# Target Groups
#
def delete_target_groups():
    """Delete all Application Load Balancers Target Groups

    :return: None
    """
    client = boto3.client('elbv2')
    print('Deleting Target Groups')
    for page in client.get_paginator('describe_target_groups').paginate():
        for target_group in page['TargetGroups']:
            target_group_arn = target_group['TargetGroupArn']
            print('Deleting Target Group {}'.format(target_group_arn))
            client.delete_target_group(
                TargetGroupArn=target_group_arn
            )
    print('Target Groups deleted')
