import pytest
import os


from common_helper_files import human_readable_file_size, read_in_chunks, get_directory_for_filename

TEST_DATA_DIR = os.path.join(get_directory_for_filename(__file__), 'data')


@pytest.mark.parametrize('input_data, expected', [
    (1000, '1000.00 Byte'),
    (1024, '1.00 KiB'),
    (1024 * 1024, '1.00 MiB'),
    (1234.1234, '1.21 KiB'),
])
def test_human_readable_file_size(input_data, expected):
    assert human_readable_file_size(input_data) == expected


def test_read_in_chunks():
    fp = open(TEST_DATA_DIR + '/read_test', 'rb')
    test_buffer = b''
    for chunk in read_in_chunks(fp):
        test_buffer += chunk
    assert test_buffer == b'this is a test'
