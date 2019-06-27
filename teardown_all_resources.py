#!/usr/bin/env python3

""" Script deleting all the resources in an AWS account.
The script will ask for confirmation before carrying on.
If the user answers 'yes', it will then proceed and delete all resources from the AWS services
supported by the script.
"""

import sys

from teardown import autoscaling, cloudtrail, ds, dynamodb, ec2, efs, elb, firehose, kinesis, kms, \
    lambda_svc, rds, redshift, route53, s3, ssm, sts, workspaces

print('Retrieving AWS account id...')
if (input(
        f"Completely delete ALL resources in account {sts.get_account_id()}? "
        f"(only 'yes' will be accepted) ") != 'yes'):
    print('Aborting...')
    sys.exit(1)

cloudtrail.delete_cloudtrails()
lambda_svc.delete_lambdas()
rds.delete_rds_instances()
autoscaling.delete_autoscaling_groups()
elb.delete_classic_load_balancers()
ec2.delete_vpc_endpoint_resources()
ec2.delete_nat_gateways()
ec2.delete_ec2_instances()
ec2.delete_amis()
ec2.delete_ebs_volumes()
elb.delete_load_balancers_v2()
workspaces.delete_workspaces()
ds.delete_directory_services()
redshift.delete_redshift_instances()
dynamodb.delete_dynamodb_instances()
efs.delete_efs_instances()
ec2.delete_network_interfaces()
ec2.delete_vpns()
ec2.delete_virtual_gateways()
ec2.delete_customer_gateways()
ec2.delete_internet_gateways()
ec2.delete_egress_only_internet_gateways()
ec2.delete_subnets()
ec2.delete_nacls()
ec2.delete_route_tables()
ec2.delete_security_groups()
ec2.delete_vpcs()
ec2.delete_elastic_ips()
ec2.delete_ssh_key_pairs()
ec2.delete_placement_groups()
elb.delete_target_groups()
ssm.delete_ssm_parameters()
kms.delete_kms_custom_keys()
kinesis.delete_kinesis_data_streams()
kinesis.delete_kinesis_applications()
firehose.delete_firehose_delivery_streams()
route53.delete_route53_zones()
s3.delete_s3_buckets()
