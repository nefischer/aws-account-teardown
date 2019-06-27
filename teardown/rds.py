"""RDS resources teardown
"""

import time
import boto3


def delete_rds_instances():
    """ Delete all RDS instances

    :return: None
    """
    print('Deleting RDS instances')
    rds = boto3.client('rds')

    for instance in rds.describe_db_instances()['DBInstances']:
        rds_instance_id = instance['DBInstanceIdentifier']
        print('Deleting RDS - {}'.format(rds_instance_id))

        rds.delete_db_instance(
            DBInstanceIdentifier=rds_instance_id,
            SkipFinalSnapshot=True,
            DeleteAutomatedBackups=True
        )

    if rds.describe_db_instances()['DBInstances']:
        print('Waiting for RDS instances to terminate')
        while rds.describe_db_instances()['DBInstances']:
            time.sleep(5)

    print('RDS instances deleted')
