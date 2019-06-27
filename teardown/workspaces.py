"""Workspaces resources teardown
"""

import time
import boto3


#
# Workspaces
#
def delete_workspaces():
    """Delete all AWS workspaces

    :return: None
    """
    print('Deleting Workspaces')
    workspaces_client = boto3.client('workspaces')
    terminating_workspaces = False

    for workspace in workspaces_client.describe_workspaces()['Workspaces']:
        ws_id = workspace['WorkspaceId']
        print('Terminating workspace {}'.format(ws_id))
        workspaces_client.terminate_workspaces(
            TerminateWorkspaceRequests=[
                {
                    'WorkspaceId': ws_id
                }
            ]
        )
        terminating_workspaces = True

    if terminating_workspaces:
        print('Waiting for the workspaces to terminate')
        while True:
            all_terminated = True
            for workspace in workspaces_client.describe_workspaces()['Workspaces']:
                if workspace['State'] != 'TERMINATED':
                    all_terminated = False
                    break
            if all_terminated:
                break
            else:
                time.sleep(5)
    print('Workspaces deleted')
