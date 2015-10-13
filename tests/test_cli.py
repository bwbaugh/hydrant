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
            input='hello world\n'):
        return runner.invoke(
            cli=cli.main,
            args=[delivery_stream],
            input=input,
        )

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
        # Given a single record
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
        )
        parameters.update(kwargs)
        return cli._get_firehose_client(**parameters)

    @pytest.mark.parametrize(
        argnames='field_name,expected_value',
        argvalues=[
            ('region_name', 'us-west-2'),
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
