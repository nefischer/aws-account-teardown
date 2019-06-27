"""EFS resources teardown
"""

import time
import boto3


#
# EFS mounts
#
def delete_efs_instances():
    """Delete all EFS instances

    :return: None
    """
    client = boto3.client('efs')

    print('Deleting EFS file systems')
    for fs_page in client.get_paginator('describe_file_systems').paginate():
        for file_system in fs_page['FileSystems']:
            fs_id = file_system['FileSystemId']
            print('Deleting EFS Mounts for {}'.format(fs_id))
            for targets_page in client.get_paginator('describe_mount_targets').paginate(
                    FileSystemId=fs_id
            ):
                for mount in targets_page['MountTargets']:
                    mount_id = mount['MountTargetId']
                    print('Deleting EFS Mount Target {}'.format(mount_id))
                    client.delete_mount_target(
                        MountTargetId=mount_id
                    )
            while client.describe_mount_targets()['MountTargets']:
                time.sleep(5)
            print('EFS Mounts deleted')
            print('Deleting EFS file system {}'.format(fs_id))
            client.delete_file_system(
                FileSystemId=fs_id
            )
    while client.describe_file_systems()['FileSystems']:
        time.sleep(5)
    print('EFS File Systems deleted')
