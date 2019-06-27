"""Route 53 resources teardown
"""

import boto3


#
# Route53
#
def delete_route53_zones():
    """Delete all Route 53 zones

    :return: None
    """
    client = boto3.client('route53')
    print('Deleting Route53 Zones')
    for zone_page in client.get_paginator('list_hosted_zones').paginate():
        for zone in zone_page['HostedZones']:
            zone_id = zone['Id']
            print('Deleting records for Hosted Zone {}'.format(zone_id))
            for record_page in client.get_paginator('list_resource_record_sets').paginate(
                    HostedZoneId=zone_id
            ):
                record_sets = record_page['ResourceRecordSets']
                changes = [
                    {
                        'Action': 'DELETE',
                        'ResourceRecordSet': record_set
                    }
                    for record_set in record_sets if
                    record_set['Type'] != 'SOA' and record_set['Type'] != 'NS'
                ]
                if changes:
                    client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch={
                            'Changes': changes
                        }
                    )

            print('Deleting Hosted Zone {}'.format(zone_id))
            client.delete_hosted_zone(
                Id=zone_id
            )

    print('Route53 Zones deleted')
