import botocore.session
import click


@click.command(epilog='Source: https://github.com/bwbaugh/hydrant')
@click.argument('delivery_stream')
@click.version_option()
def main(delivery_stream):
    """Redirects stdin to Amazon Kinesis Firehose.

    Records will be written to DELIVERY_STREAM. Data should be
    separated by a newline character. Each line will be sent as a
    separate record, so keep in mind that Kinesis Firehose will round
    up each record to the next 5 KB in size.
    """
    client = _get_firehose_client()
    for line in click.get_binary_stream('stdin'):
        client.put_record(
            DeliveryStreamName=delivery_stream,
            Record={'Data': line},
        )


def _get_firehose_client():
    session = botocore.session.get_session()
    client = session.create_client(
        service_name='firehose',
        region_name='us-west-2',
    )
    return client
