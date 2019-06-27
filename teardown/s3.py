"""S3 resources teardown
"""

import boto3


#
# S3 Buckets
#
def delete_s3_buckets():
    """Delete all S3 buckets

    :return: None
    """
    s3_resource = boto3.resource('s3')
    print('Deleting S3 Buckets')
    for bucket in s3_resource.buckets.all():
        print('Starting object deletion for S3 Bucket {}'.format(bucket.name))
        bucket.object_versions.delete()
        print('Deleting S3 Bucket {}'.format(bucket.name))
        bucket.delete()
    print('S3 Buckets deleted')
