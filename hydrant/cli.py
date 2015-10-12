import click


@click.command(epilog='Source: https://github.com/bwbaugh/hydrant')
@click.version_option()
def main():
    """Redirects stdin to Amazon Kinesis Firehose."""
    pass
