import botocore.session
import click.testing
import mock
import pytest

from hydrant import cli


@pytest.fixture
def mock_firehose_client():
    return mock.Mock(name='firehose_client', spec=['put_record'])


@pytest.mark.usefixtures('patch_get_firehose_client')
class TestMain(object):

    @pytest.fixture
    def runner(self):
        return click.testing.CliRunner()

    @pytest.fixture
    def patch_get_firehose_client(self, request, mock_firehose_client):
        patcher = mock.patch.object(
            cli,
            '_get_firehose_client',
            autospec=True,
            return_value=mock_firehose_client,
        )
        mock_instance = patcher.start()
        request.addfinalizer(patcher.stop)
        return mock_instance

    def _call(
            self, runner, delivery_stream='my-test-delivery-stream-name',
            input='hello world\n', region=None, print_record_id=None):
        args = []
        if region is not None:
            args.extend(['--region', region])
        if print_record_id is True:
            args.append('--print-record-id')
        elif print_record_id is False:
            args.append('--no-print-record-id')
        args.append(delivery_stream)
        return runner.invoke(
            cli=cli.main,
            args=args,
            input=input,
        )

    def test_client_region_default(self, runner, patch_get_firehose_client):
        # When we run the command
        result = self._call(runner=runner)
        # Then there should be no errors
        assert result.exit_code == 0
        assert not result.exception
        # And the client should use the default region
        assert patch_get_firehose_client.call_count == 1
        args, kwargs = patch_get_firehose_client.call_args
        assert kwargs['region_name'] == cli.DEFAULT_AWS_REGION

    def test_client_region_override(self, runner, patch_get_firehose_client):
        # Given a region
        region = 'us-west-2'
        # When we run the command
        result = self._call(runner=runner, region=region)
        # Then there should be no errors
        assert result.exit_code == 0
        assert not result.exception
        # And the client should use the requested region
        assert patch_get_firehose_client.call_count == 1
        args, kwargs = patch_get_firehose_client.call_args
        assert kwargs['region_name'] == region

    def test_delivery_stream_name(self, runner, mock_firehose_client):
        # Given a delivery stream name
        delivery_stream = 'my-test-delivery-stream-name'
        # When we run the command
        result = self._call(runner=runner, delivery_stream=delivery_stream)
        # Then there should be no errors
        assert result.exit_code == 0
        assert not result.exception
        # And a record should be sent to the delivery stream
        assert mock_firehose_client.put_record.call_count == 1
        args, kwargs = mock_firehose_client.put_record.call_args
        assert kwargs['DeliveryStreamName'] == delivery_stream

    def test_one_record(self, runner, mock_firehose_client):
        # Given a single record
        stdin = 'hello world\n'
        # When we run the command
        result = self._call(runner=runner, input=stdin)
        # Then there should be no errors
        assert result.exit_code == 0
        assert not result.exception
        # And a record should be sent with the data from stdin
        assert mock_firehose_client.put_record.call_count == 1
        args, kwargs = mock_firehose_client.put_record.call_args
        assert kwargs['Record'] == {'Data': stdin}

    def test_two_records(self, runner, mock_firehose_client):
        # Given two records
        stdin = 'foo\nbar\n'
        # When we run the command
        result = self._call(runner=runner, input=stdin)
        # Then there should be no errors
        assert result.exit_code == 0
        assert not result.exception
        # And a each line should result in a record
        assert mock_firehose_client.put_record.call_count == 2
        args, kwargs = mock_firehose_client.put_record.call_args_list[0]
        assert kwargs['Record'] == {'Data': 'foo\n'}
        args, kwargs = mock_firehose_client.put_record.call_args_list[1]
        assert kwargs['Record'] == {'Data': 'bar\n'}

    def test_print_record_id(self, runner, mock_firehose_client):
        # Given multiple records
        stdin = 'hello world\n' * 3
        # And the print record-ID flag is enabled
        print_record_id = True
        # And a fake record-ID is generated for each record

        def fake_id_generator(*args, **kwargs):
            counter = 1
            while True:
                yield {'RecordId': unicode(counter)}
                counter += 1
        mock_firehose_client.put_record.side_effect = iter(fake_id_generator())
        # When we run the command
        result = self._call(
            runner=runner,
            input=stdin,
            print_record_id=print_record_id,
        )
        # Then there should be no errors
        assert result.exit_code == 0
        assert not result.exception
        # And the record-ID should be printed for each input line
        assert result.output == '1\n2\n3\n'

    def test_no_print_record_id(self, runner, mock_firehose_client):
        # Given multiple records
        stdin = 'hello world\n' * 3
        # But the print record-ID flag is disabled
        print_record_id = False
        # When we run the command
        result = self._call(
            runner=runner,
            input=stdin,
            print_record_id=print_record_id,
        )
        # Then there should be no errors
        assert result.exit_code == 0
        assert not result.exception
        # And the record-ID should not be printed
        assert not result.output


@pytest.mark.usefixtures('patch_get_session')
class TestGetFirehoseClient(object):

    @pytest.fixture
    def patch_get_session(self, request, mock_session):
        patcher = mock.patch.object(
            cli.botocore.session,
            'get_session',
            autospec=True,
            return_value=mock_session,
        )
        mock_instance = patcher.start()
        request.addfinalizer(patcher.stop)
        return mock_instance

    @pytest.fixture
    def mock_session(self, mock_firehose_client):
        session = mock.create_autospec(botocore.session.Session)
        session.create_client.return_value = mock_firehose_client
        return session

    def _call(self, **kwargs):
        parameters = dict(
            region_name=mock.sentinel.region_name,
        )
        parameters.update(kwargs)
        return cli._get_firehose_client(**parameters)

    @pytest.mark.parametrize(
        argnames='field_name,expected_value',
        argvalues=[
            ('region_name', mock.sentinel.region_name),
            ('service_name', 'firehose'),
        ],
        ids=['service_name', 'region_name'],
    )
    def test_calls_create_client(
            self, mock_session, field_name, expected_value):
        # When we get the client
        self._call()
        # Then the "<field_name>" should be "<expected_value>"
        assert mock_session.create_client.call_count == 1
        args, kwargs = mock_session.create_client.call_args
        assert kwargs[field_name] == expected_value

    def test_returns_client(self, mock_firehose_client):
        # When we get the client
        result = self._call()
        # Then the client should be returned
        assert result is mock_firehose_client
