
from mock import patch

import mock

from .test_helper import *

from kiwi.utils.compress import Compress
from kiwi.exceptions import *


class TestCompress(object):
    @patch('os.path.exists')
    def setup(self, mock_exists):
        mock_exists.return_value = True
        self.compress = Compress('some-file', True)

    @raises(KiwiFileNotFound)
    def test_source_file_not_found(self):
        Compress('some-file')

    @patch('kiwi.command.Command.run')
    def test_xz(self, mock_command):
        self.compress.xz()
        mock_command.assert_called_once_with(
            [
                'xz', '-f', '--check=crc32', '--lzma2=dict=512KiB', '--keep',
                'some-file'
            ]
        )
        assert self.compress.compressed_filename == 'some-file.xz'

    @patch('kiwi.command.Command.run')
    def test_gzip(self, mock_command):
        self.compress.gzip()
        mock_command.assert_called_once_with(
            ['gzip', '-f', '-9', '--keep', 'some-file']
        )
        assert self.compress.compressed_filename == 'some-file.gz'

    @patch('kiwi.command.Command.run')
    @patch('kiwi.utils.compress.NamedTemporaryFile')
    @patch('kiwi.utils.compress.Compress.get_format')
    def test_uncompress(self, mock_format, mock_temp, mock_command):
        mock_format.return_value = 'xz'
        self.compress.uncompress()
        mock_command.assert_called_once_with(
            ['xz', '-d', 'some-file']
        )
        assert self.compress.uncompressed_filename == 'some-file'

    @patch('kiwi.command.Command.run')
    @patch('kiwi.utils.compress.NamedTemporaryFile')
    @patch('kiwi.utils.compress.Compress.get_format')
    def test_uncompress_temporary(self, mock_format, mock_temp, mock_command):
        tempfile = mock.Mock()
        tempfile.name = 'tempfile'
        mock_temp.return_value = tempfile
        mock_format.return_value = 'xz'
        self.compress.uncompress(temporary=True)
        mock_command.assert_called_once_with(
            ['bash', '-c', 'xz -c -d some-file > tempfile']
        )
        assert self.compress.uncompressed_filename == 'tempfile'

    @raises(KiwiCompressionFormatUnknown)
    @patch('kiwi.utils.compress.Compress.get_format')
    def test_uncompress_unknown_format(self, mock_format):
        mock_format.return_value = None
        self.compress.uncompress()

    def test_get_format(self):
        xz = Compress('../data/xz_data.xz')
        assert xz.get_format() == 'xz'
        gzip = Compress('../data/gz_data.gz')
        assert gzip.get_format() == 'gzip'
