"""STS resources teardown
"""

import boto3


def get_account_id():
    """Retrieves the id of the current AWS account - the one associated with the credentials
    being used.

    :return: the AWS account id
    """
    return boto3.client("sts").get_caller_identity()["Account"]
