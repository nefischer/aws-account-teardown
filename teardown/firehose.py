"""Firehose resources teardown
"""

import time
import boto3


#
# Firehose Delivery Streams
#
def delete_firehose_delivery_streams():
    """Delete all Firehose delivery streams

    :return: None
    """
    client = boto3.client('firehose')
    print('Deleting Firehose Delivery Streams')
    list_delivery_streams_resp = client.list_delivery_streams()
    start_from_stream = None
    while True:
        for name in list_delivery_streams_resp['DeliveryStreamNames']:
            print('Deleting Firehose Delivery Stream {}'.format(name))
            client.delete_delivery_stream(
                DeliveryStreamName=name,
            )
            start_from_stream = name
        if list_delivery_streams_resp['HasMoreDeliveryStreams'] and start_from_stream:
            list_delivery_streams_resp = client.list_delivery_streams(
                ExclusiveStartDeliveryStreamName=start_from_stream
            )
        else:
            break
    while client.list_delivery_streams()['DeliveryStreamNames']:
        time.sleep(5)
    print('Firehose Delivery Streams deleted')
