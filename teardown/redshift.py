"""Redshift resources teardown
"""

import time
import boto3


#
# Redshift
#
def delete_redshift_instances():
    """ Delete all RedShift instances

    :return: None
    """
    print('Deleting Redshift clusters')
    client = boto3.client('redshift')
    for page in client.get_paginator('describe_clusters').paginate():
        for cluster in page['Clusters']:
            cluster_id = cluster['ClusterIdentifier']
            print('Deleting Redshift cluster {}'.format(cluster_id))
            client.delete_cluster(
                ClusterIdentifier=cluster_id,
                SkipFinalClusterSnapshot=True
            )
    while client.describe_clusters()['Clusters']:
        time.sleep(5)
    print('Redshift clusters deleted')

    print('Deleting Redshift snapshots')
    for page in client.get_paginator('describe_cluster_snapshots').paginate():
        for snapshot in page['Snapshots']:
            snapshot_id = snapshot['SnapshotIdentifier']
            print('Deleting Redshift snapshot {}'.format(snapshot_id))
            client.delete_cluster_snapshot(
                SnapshotIdentifier=snapshot_id
            )
    while client.describe_cluster_snapshots()['Snapshots']:
        time.sleep(5)
    print('Redshift snapshots deleted')
