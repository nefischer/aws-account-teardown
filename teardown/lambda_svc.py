"""Lambda Services resources teardown
"""

import time
import boto3


#
# Lambdas
#
def delete_lambdas():
    """Delete all Lambda functions

    :return: None
    """
    print('Deleting Lambdas')
    client = boto3.client('lambda')
    func_list_resp = client.list_functions(
        MaxItems=50
    )
    while True:
        for func in func_list_resp['Functions']:
            func_name = func['FunctionName']
            print('Deleting Lambda {}'.format(func_name))
            client.delete_function(
                FunctionName=func_name
            )

        if 'NextMarker' in func_list_resp:
            func_list_resp = client.list_functions(
                Marker=func_list_resp['NextMarker'],
                MaxItems=50
            )
        else:
            break

    while client.list_functions()['Functions']:
        time.sleep(5)
    print('Lambdas deleted')
