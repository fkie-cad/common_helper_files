import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from common_helper_files import (
    create_symlink, delete_file, get_safe_name, get_binary_from_file, get_dir_of_file, get_directory_for_filename,
    get_dirs_in_dir, get_files_in_dir, get_string_list_from_file, safe_rglob, write_binary_to_file
)
from common_helper_files.fail_safe_file_operations import _get_counted_file_path, _rm_cr


EMPTY_FOLDER = Path(get_directory_for_filename(__file__)).parent / 'tests' / 'data' / 'empty_folder'
EMPTY_FOLDER.mkdir(exist_ok=True)


class TestFailSafeFileOperations(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = TemporaryDirectory(prefix="test_common_helper_file")

    def tearDown(self):
        self.tmp_dir.cleanup()

    @staticmethod
    def get_directory_of_current_file():
        return get_directory_for_filename(__file__)

    def test_fail_safe_read_file(self):
        test_file_path = os.path.join(self.get_directory_of_current_file(), "data", "read_test")
        file_binary = get_binary_from_file(test_file_path)
        self.assertEqual(file_binary, b'this is a test', "content not correct")
        # Test none existing file
        none_existing_file_path = os.path.join(self.get_directory_of_current_file(), "data", "none_existing_file")
        file_binary = get_binary_from_file(none_existing_file_path)
        self.assertEqual(file_binary, b'', "content not correct")
        # Test link
        link_path = os.path.join(self.get_directory_of_current_file(), "data", "link_test")
        file_binary = get_binary_from_file(link_path)
        assert file_binary == 'symbolic link -> read_test'

    def test_fail_safe_read_file_string_list(self):
        test_file_path = os.path.join(self.get_directory_of_current_file(), "data", "multiline_test.txt")
        lines = get_string_list_from_file(test_file_path)
        self.assertEqual(lines, ['first line', 'second line', 'th\ufffdrd line', '', 'first line'], "lines not correct")

    def test_fail_safe_write_file(self):
        file_path = os.path.join(self.tmp_dir.name, "test_folder", "test_file")
        write_binary_to_file(b'this is a test', file_path)
        self.assertTrue(os.path.exists(file_path), "file not created")
        read_binary = get_binary_from_file(file_path)
        self.assertEqual(read_binary, b'this is a test', "written data not correct")
        # Test not overwrite flag
        write_binary_to_file(b'do not overwrite', file_path, overwrite=False)
        read_binary = get_binary_from_file(file_path)
        self.assertEqual(read_binary, b'this is a test', "written data not correct")
        # Test overwrite flag
        write_binary_to_file(b'overwrite', file_path, overwrite=True)
        read_binary = get_binary_from_file(file_path)
        self.assertEqual(read_binary, b'overwrite', "written data not correct")
        # Test copy_file_flag
        write_binary_to_file(b'second_overwrite', file_path, file_copy=True)
        self.assertTrue(os.path.exists("{}-1".format(file_path)), "new file copy does not exist")
        read_binary_original = get_binary_from_file(file_path)
        self.assertEqual(read_binary_original, b'overwrite', "original file no longer correct")
        read_binary_new = get_binary_from_file("{}-1".format(file_path))
        self.assertEqual(read_binary_new, b'second_overwrite', "binary of new file not correct")

    def test_get_counted_file_path(self):
        self.assertEqual(_get_counted_file_path("/foo/bar"), "/foo/bar-1", "simple case")
        self.assertEqual(_get_counted_file_path("/foo/bar-11"), "/foo/bar-12", "simple count two digits")
        self.assertEqual(_get_counted_file_path("foo-34/bar"), "foo-34/bar-1", "complex case")

    def test_delete_file(self):
        file_path = os.path.join(self.tmp_dir.name, "test_folder", "test_file")
        write_binary_to_file(b'this is a test', file_path)
        self.assertTrue(os.path.exists(file_path), "file not created")
        delete_file(file_path)
        self.assertFalse(os.path.exists(file_path))
        # Test delete none existing file
        delete_file(file_path)

    def test_create_symlink(self):
        test_file_path = os.path.join(self.tmp_dir.name, 'test_folder', 'test_file')
        symlink_path = os.path.join(self.tmp_dir.name, 'test_symlink')
        create_symlink(test_file_path, symlink_path)
        self.assertEqual(os.readlink(symlink_path), test_file_path)
        symlink_path_none_existing_dir = os.path.join(self.tmp_dir.name, 'some_dir/test_symlink')
        create_symlink(test_file_path, symlink_path_none_existing_dir)
        self.assertEqual(os.readlink(symlink_path_none_existing_dir), test_file_path)
        # check error handling
        create_symlink(test_file_path, symlink_path)

    def test_get_safe_name(self):
        a = "/()=Hello%&World!? Foo"
        self.assertEqual(get_safe_name(a), "HelloWorld_Foo", "result not correct")
        b = 250 * 'a'
        self.assertEqual(len(get_safe_name(b)), 200, "lenght not cutted correctly")

    def test_get_files_in_dir(self):
        test_dir_path = os.path.join(self.get_directory_of_current_file(), "data")
        result = get_files_in_dir(test_dir_path)
        self.assertIn(os.path.join(test_dir_path, "read_test"), result, "file in root folder not found")
        self.assertIn(os.path.join(test_dir_path, "test_folder/generic_test_file"), result, "file in sub folder not found")
        self.assertEqual(len(result), 6, "number of found files not correct")

    def test_get_files_in_dir_error(self):
        result = get_files_in_dir("/none_existing/dir")
        self.assertEqual(result, [], "error result should be an empty list")

    def test_get_dirs(self):
        test_dirs = ["dir_1", "dir_2", "dir_1/sub_dir"]
        for item in test_dirs:
            os.mkdir(os.path.join(self.tmp_dir.name, item))
        result = get_dirs_in_dir(self.tmp_dir.name)
        self.assertEqual(sorted(result), [os.path.join(self.tmp_dir.name, "dir_1"), os.path.join(self.tmp_dir.name, "dir_2")], "found dirs not correct")

    def test_get_dirs_in_dir_error(self):
        result = get_dirs_in_dir("/none_existing/dir")
        self.assertEqual(result, [], "error result should be an empty list")

    def test_get_dir_of_file_relative_path(self):
        relative_path_result = get_dir_of_file("test/some_file")
        expected_result = os.path.join(os.getcwd(), "test")
        self.assertEqual(relative_path_result, expected_result)

    def test_get_dir_of_file_absolute_path(self):
        test_file_path = os.path.join(self.tmp_dir.name, 'test_file')
        write_binary_to_file('test', test_file_path)
        absolute_file_path_result = get_dir_of_file(test_file_path)
        self.assertEqual(absolute_file_path_result, self.tmp_dir.name)


@pytest.mark.parametrize('symlinks, directories, expected_number', [
    (True, True, 7),
    (False, True, 5),
    (True, False, 5),
    (False, False, 3),
])
def test_safe_rglob(symlinks, directories, expected_number):
    test_dir_path = Path(TestFailSafeFileOperations.get_directory_of_current_file()).parent / 'tests' / 'data'
    result = list(safe_rglob(test_dir_path, include_symlinks=symlinks, include_directories=directories))
    assert len(result) == expected_number


def test_safe_rglob_invalid_path():
    test_path = Path('foo', 'bar')
    assert not test_path.exists()
    result = safe_rglob(test_path)
    assert len(list(result)) == 0


def test_safe_rglob_empty_dir():
    assert EMPTY_FOLDER.exists()
    result = safe_rglob(EMPTY_FOLDER)
    assert len(list(result)) == 0


@pytest.mark.parametrize('input_data, expected', [
    ('abc', 'abc'),
    ('ab\r\nc', 'ab\nc')])
def test_rm_cr(input_data, expected):
    assert _rm_cr(input_data) == expected
