"""EC2 resources teardown
"""

import time
import boto3
from .sts import get_account_id


def delete_vpc_endpoint_resources():
    """Delete all the VPC endpoints

    :return: None
    """
    print('Deleting VPC endpoints')
    ec2 = boto3.client('ec2')
    endpoint_ids = []
    for endpoint in ec2.describe_vpc_endpoints()['VpcEndpoints']:
        print('Deleting VPC Endpoint - {}'.format(endpoint['ServiceName']))
        endpoint_ids.append(endpoint['VpcEndpointId'])

    if endpoint_ids:
        ec2.delete_vpc_endpoints(
            VpcEndpointIds=endpoint_ids
        )

        print('Waiting for VPC endpoints to get deleted')
        while ec2.describe_vpc_endpoints()['VpcEndpoints']:
            time.sleep(5)

    print('VPC endpoints deleted')

    # VPC endpoints connections
    print('Deleting VPC endpoint connections')
    service_ids = []
    for connection in ec2.describe_vpc_endpoint_connections()['VpcEndpointConnections']:
        service_id = connection['ServiceId']
        state = connection['VpcEndpointState']

        if state in ['PendingAcceptance', 'Pending', 'Available', 'Rejected', 'Failed', 'Expired']:
            print('Deleting VPC Endpoint Service - {}'.format(service_id))
            service_ids.append(service_id)

            ec2.reject_vpc_endpoint_connections(
                ServiceId=service_id,
                VpcEndpointIds=[
                    connection['VpcEndpointId'],
                ]
            )

    if service_ids:
        ec2.delete_vpc_endpoint_service_configurations(
            ServiceIds=service_ids
        )

        print('Waiting for VPC endpoint services to be destroyed')
        while ec2.describe_vpc_endpoint_connections()['VpcEndpointConnections']:
            time.sleep(5)

    print('VPC endpoint connections deleted')


#
# NAT gateways
#
def delete_nat_gateways():
    """Delete all the NAT gateways

    :return: None
    """
    print('Deleting NAT gateways')
    ec2 = boto3.client('ec2')
    for page in ec2.get_paginator('describe_nat_gateways').paginate():
        for nat_gateway in page['NatGateways']:
            nat_gateway_id = nat_gateway['NatGatewayId']
            print('Deleting Nat Gateway - {}'.format(nat_gateway_id))
            ec2.delete_nat_gateway(
                NatGatewayId=nat_gateway_id
            )

    while ec2.describe_nat_gateways()['NatGateways']:
        all_deleted = True
        for gateway in ec2.describe_nat_gateways()['NatGateways']:
            if gateway['State'] != 'deleted':
                all_deleted = False
                break
        if all_deleted:
            break
        else:
            time.sleep(5)

    print('NAT gateways deleted')


#
# EC2 instances
#
def delete_ec2_instances():
    """Delete all the EC2 instances

    :return: None
    """
    print('Deleting EC2 instances')
    ec2 = boto3.resource('ec2')

    active_ec2_instance_count = 0
    for instance in ec2.instances.all():
        disable_api_termination = instance.describe_attribute(
            Attribute='disableApiTermination'
        )
        if disable_api_termination['DisableApiTermination']['Value']:
            print('Stopping instance to enable API termination - {}'.format(instance.instance_id))
            instance.stop()
            active_ec2_instance_count = active_ec2_instance_count + 1
        else:
            if instance.state['Code'] != 48:  # code 48 is 'terminated'
                print('Terminating instance - {}'.format(instance.instance_id))
                instance.terminate()
                active_ec2_instance_count = active_ec2_instance_count + 1

    if active_ec2_instance_count > 0:
        print('Waiting for ec2 instances to stop or terminate')
        while [instance for instance in ec2.instances.all()]:
            all_terminated = True
            for instance in ec2.instances.all():
                disable_api_termination = instance.describe_attribute(
                    Attribute='disableApiTermination'
                )
                if (disable_api_termination['DisableApiTermination']['Value'] and
                        instance.state['Code'] == 80):
                    # code 80 is 'stopped'
                    # instance has termination protection switched on and is stopped
                    # switch it off and terminate the instance
                    instance.modify_attribute(
                        DisableApiTermination={
                            'Value': False
                        }
                    )
                    instance.terminate()
                if instance.state['Code'] != 48:  # code 48 is 'terminated'
                    all_terminated = False

            if all_terminated:
                break
            else:
                time.sleep(5)

    print('EC2 instances deleted')


#
# EBS Volumes
#
def delete_ebs_volumes():
    """Delete all the EBS volumes

    :return: None
    """
    client = boto3.client('ec2')

    print('Deleting EBS volumes')
    volumes_resp = client.describe_volumes(
        MaxResults=500
    )
    while True:
        for vol in volumes_resp['Volumes']:
            volume_id = vol['VolumeId']
            print('Deleting Volume {}'.format(volume_id))
            client.delete_volume(
                VolumeId=volume_id
            )
            time.sleep(0.25)  # REST API is throttled
        if 'NextMarker' in volumes_resp:
            volumes_resp = client.describe_volumes(
                Marker=volumes_resp['NextMarker'],
                MaxResults=500
            )
        else:
            break

    while client.describe_volumes()['Volumes']:
        time.sleep(5)
    print('EBS volumes deleted')

    print('Deleting EBS snapshots')
    for page in client.get_paginator('describe_snapshots').paginate(
            OwnerIds=[get_account_id()]
    ):
        for snapshot in page['Snapshots']:
            snapshot_id = snapshot['SnapshotId']
            print('Deleting EBS snapshot {}'.format(snapshot_id))
            client.delete_snapshot(
                SnapshotId=snapshot_id,
            )
    while client.describe_snapshots(
            OwnerIds=[get_account_id()]
    )['Snapshots']:
        time.sleep(5)

    print('EBS snapshots deleted')


def delete_amis():
    """Delete all AMIs

    :return: None
    """
    client = boto3.client('ec2')
    account_id = get_account_id()

    print('Deleting AMIs')
    image_resp = client.describe_images(
        Owners=[account_id]
    )
    while True:
        for image in image_resp['Images']:
            image_id = image['ImageId']
            print('Deregistering AMI {}'.format(image_id))
            client.deregister_image(
                ImageId=image_id
            )

        if 'NextMarker' in image_resp:
            image_resp = client.describe_images(
                Marker=image_resp['NextMarker'],
                Owners=[account_id]
            )
        else:
            break
    while client.describe_images(
            Owners=[account_id]
    )['Images']:
        time.sleep(5)
    print('AMIs deleted')


#
# Network interfaces
#
def delete_network_interfaces():
    """Delete all network interfaces

    :return: None
    """
    print('Deleting Network Interfaces')
    ec2 = boto3.resource('ec2')
    for interface in ec2.network_interfaces.all():
        print('Deleting interface - {}'.format(interface.id))
        interface.delete()

    if [ni for ni in ec2.network_interfaces.all()]:
        print('Waiting for network interfaces to be destroyed')
        while ec2.network_interfaces.all():
            time.sleep(5)
    print('Network Interfaces deleted')


#
# VPCs
#
def delete_vpcs():
    """ Delete all VPCs

    :return: None
    """
    print('Deleting VPCs')
    client = boto3.resource('ec2')
    for vpc in client.vpcs.all():
        print('Deleting peering connections for VPC {}'.format(vpc.id))
        for peering_connection in vpc.requested_vpc_peering_connections.all():
            peering_connection.delete()

        for peering_connection in vpc.accepted_vpc_peering_connections.all():
            peering_connection.delete()
        print('Peering connections for VPC {} deleted'.format(vpc.id))

        if not vpc.is_default:
            print('Deleting vpc {}'.format(vpc.id))
            vpc.delete()
    print('VPCs deleted')


#
# Virtual Gateways
#
def delete_virtual_gateways():
    """Delete all Virtual Gateways

    :return: None
    """
    client = boto3.client('ec2')
    print('Deleting VPN Gateways')
    gw_resp = client.describe_vpn_gateways()
    while True:
        for gateway in gw_resp['VpnGateways']:
            gw_id = gateway['VpnGatewayId']
            gw_attachments = gateway['VpcAttachments']
            for attachment in gw_attachments:
                if attachment['State'] == 'attached':
                    vpc_id = attachment['VpcId']
                    print('Detaching virtual gateway {} from vpc {}'.format(gw_id, vpc_id))
                    client.detach_vpn_gateway(
                        VpcId=vpc_id,
                        VpnGatewayId=gw_id
                    )
            print('Deleting VPN gateway {}'.format(gw_id))
            client.delete_vpn_gateway(
                VpnGatewayId=gw_id
            )
        if 'NextMarker' in gw_resp:
            gw_resp = client.describe_vpn_gateways(
                Marker=gw_resp['NextMarker'],
            )
        else:
            break
    while client.describe_vpn_gateways()['VpnGateways']:
        all_deleted = True
        for gateway in client.describe_vpn_gateways()['VpnGateways']:
            if gateway['State'] != 'deleted':
                all_deleted = False
                break
        if all_deleted:
            break
        else:
            time.sleep(5)
    print('VPN Gateways deleted')


#
# Customer Gateways
#
def delete_customer_gateways():
    """Delete all Customer Gateways

    :return: None
    """
    client = boto3.client('ec2')
    print('Deleting Customer Gateways')
    cust_resp = client.describe_customer_gateways()
    while True:
        for gateway in cust_resp['CustomerGateways']:
            gw_id = gateway['CustomerGatewayId']
            client.delete_customer_gateway(
                CustomerGatewayId=gw_id
            )
            time.sleep(0.25)
        if 'NextMarker' in cust_resp:
            cust_resp = client.describe_customer_gateways(
                Marker=cust_resp['NextMarker'],
            )
        else:
            break
    while client.describe_customer_gateways()['CustomerGateways']:
        all_deleted = True
        for gateway in client.describe_customer_gateways()['CustomerGateways']:
            if gateway['State'] != 'deleted':
                all_deleted = False
                break
        if all_deleted:
            break
        else:
            time.sleep(5)
    print('Customer Gateways deleted')


#
# VPNs
#
def delete_vpns():
    """Delete all VPNs

    :return: None
    """
    client = boto3.client('ec2')
    print('Deleting VPNs')
    vpn_resp = client.describe_vpn_connections()
    while True:
        for vpn in vpn_resp['VpnConnections']:
            vpn_id = vpn['VpnConnectionId']
            print('Deleting VPN {}'.format(vpn_id))
            client.delete_vpn_connection(
                VpnConnectionId=vpn_id
            )
        if 'NextMarker' in vpn_resp:
            vpn_resp = client.describe_vpn_connections(
                Marker=vpn_resp['NextMarker'],
            )
        else:
            break
    while client.describe_vpn_connections()['VpnConnections']:
        all_deleted = True
        for vpn in client.describe_vpn_connections()['VpnConnections']:
            if vpn['State'] != 'deleted':
                all_deleted = False
                break
        if all_deleted:
            break
        else:
            time.sleep(5)
    print('VPN deleted')


#
# Subnets
#
def delete_subnets():
    """Delete all subnets

    :return: None
    """
    print('Deleting Subnets')
    client = boto3.resource('ec2')
    for subnet in client.subnets.all():
        print('Deleting subnet {}'.format(subnet.id))
        subnet.delete()
    print('Subnets deleted')


#
# Network ACLs
#
def delete_nacls():
    """Delete all NACLs

    :return: None
    """
    print('Deleting NACLs')
    client = boto3.resource('ec2')
    for nacl in client.network_acls.all():
        if nacl.is_default:
            # can't delete default NACL so delete all the rules
            for entry in nacl.entries:
                rule_number = entry['RuleNumber']
                egress = entry['Egress']
                if rule_number < 32766:  # max value for custom rule number
                    print('Deleting {} entry {} for default NACL {}'.format(
                        'egress' if egress else 'ingress',
                        rule_number, nacl.id))
                    nacl.delete_entry(
                        RuleNumber=rule_number,
                        Egress=egress
                    )
        else:
            print('Deleting NACL {}'.format(nacl.id))
            nacl.delete()
    print('NACLs deleted')


#
# Internet Gateways
#
def delete_internet_gateways():
    """Delete all Internet Gateways

    :return: None
    """
    print('Deleting Internet Gateways')
    client = boto3.resource('ec2')
    for igw in client.internet_gateways.all():
        for attachment in igw.attachments:
            if 'State' in attachment and attachment['State'] == 'available':
                vpc_id = attachment['VpcId']
                print('Detaching internet gateway {} from vpc {}'.format(igw.id, vpc_id))
                igw.detach_from_vpc(
                    VpcId=vpc_id
                )
        print('Deleting Internet Gateway {}'.format(igw.id))
        igw.delete()

    while [igw for igw in client.internet_gateways.all()]:
        time.sleep(5)
    print('Internet Gateways deleted')


#
# Egress only internet gateways
#
def delete_egress_only_internet_gateways():
    """Delete all Egress Only Internet Gateways

    :return: None
    """
    client = boto3.client('ec2')
    print('Deleting Egress Only Internet Gateways')
    gw_resp = client.describe_egress_only_internet_gateways()
    while True:
        for gateway in gw_resp['EgressOnlyInternetGateways']:
            gw_id = gateway['EgressOnlyInternetGatewayId']
            client.delete_egress_only_internet_gateway(
                EgressOnlyInternetGatewayId=gw_id
            )
        if 'NextMarker' in gw_resp:
            gw_resp = client.describe_egress_only_internet_gateways(
                Marker=gw_resp['NextMarker'],
            )
        else:
            break
    while client.describe_egress_only_internet_gateways()['EgressOnlyInternetGateways']:
        time.sleep(5)
    print('Egress Only Internet Gateways deleted')


#
# Route Tables
#
def delete_route_tables():
    """Delete the route tables

    :return: None
    """
    client = boto3.resource('ec2')
    print('Deleting Route Tables')
    for route_table in client.route_tables.all():
        for route in route_table.routes:
            if route.origin == 'CreateRoute':
                print('Deleting Route {} in Route Table {}'.format(route.destination_cidr_block,
                                                                   route_table.id))
                route.delete()
        main = False
        for rta in route_table.associations:
            if rta.main:
                main = True
            else:
                print('Deleting Route Table Association {}'.format(rta.id))
                rta.delete()
        if not main:
            print('Deleting Route Table {}'.format(route_table.id))
            route_table.delete()
    print('Route Tables deleted')


#
# Security Groups
#
def delete_security_groups():
    """Delete all security groups

    :return: None
    """
    print('Deleting Security Groups')
    client = boto3.resource('ec2')
    for security_group in client.security_groups.all():
        print('Deleting Security Group rules for security group {}'.format(security_group.id))
        for perm in security_group.ip_permissions:
            security_group.revoke_ingress(
                IpPermissions=[perm]
            )
        for perm in security_group.ip_permissions_egress:
            security_group.revoke_egress(
                IpPermissions=[perm]
            )
    for security_group in client.security_groups.all():
        if security_group.group_name != 'default':
            print('Deleting Security Group {}'.format(security_group.id))
            security_group.delete()
    print('Security Groups deleted')


#
# Elastic IP addresses
#
def delete_elastic_ips():
    """Delete all Elastic IPs

    :return: None
    """
    client = boto3.client('ec2')
    print('Deleting Elastic IPs')
    for eip in client.describe_addresses()['Addresses']:
        allocation_id = eip['AllocationId']
        print('Releasing EIP {}'.format(allocation_id))
        client.release_address(
            AllocationId=allocation_id
        )

    print('Elastic IPs deleted')


#
# SSH Key Pairs
#
def delete_ssh_key_pairs():
    """Delete all SSH key pairs

    :return: None
    """
    client = boto3.resource('ec2')
    print('Deleting SSH Key Pairs')
    for key in client.key_pairs.all():
        print('Deleting SSH Key Pair {}'.format(key.name))
        key.delete()
    print('SSH Key Pairs deleted')


#
# Placement Groups
#
def delete_placement_groups():
    """Delete all placement groups

    :return: None
    """
    client = boto3.resource('ec2')
    print('Deleting Placement Groups')
    for placement_group in client.placement_groups.all():
        print('Deleting Placement Group {}'.format(placement_group.name))
        placement_group.delete()
    print('Placement Groups deleted')
