import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from common_helper_files import (
    create_symlink, delete_file, get_safe_name, get_binary_from_file, get_dir_of_file, get_directory_for_filename,
    get_dirs_in_dir, get_files_in_dir, get_string_list_from_file, safe_rglob, write_binary_to_file
)
from common_helper_files.fail_safe_file_operations import _get_counted_file_path

TEST_DATA_DIR = Path(__file__).absolute().parent / 'data'
EMPTY_FOLDER = TEST_DATA_DIR / 'empty_folder'
EMPTY_FOLDER.mkdir(exist_ok=True)


@pytest.fixture(scope="function")
def tempdir():
    tmp_dir = None
    try:
        tmp_dir = TemporaryDirectory(prefix="test_common_helper_file")
        yield tmp_dir
    finally:
        if tmp_dir:
            tmp_dir.cleanup()


@pytest.fixture(scope="module")
def create_symlinks():
    recursive_broken_link = TEST_DATA_DIR / "recursive_broken_link"
    broken_link = TEST_DATA_DIR / "broken_link"
    try:
        if not recursive_broken_link.is_symlink():
            recursive_broken_link.symlink_to("recursive_broken_link")
        if not broken_link.is_symlink():
            broken_link.symlink_to("nonexistent")
        yield
    finally:
        if recursive_broken_link.is_symlink():
            recursive_broken_link.unlink()
        if broken_link.is_symlink():
            broken_link.unlink()


def get_directory_of_current_file():
    return get_directory_for_filename(__file__)


def test_fail_safe_read_file():
    test_file_path = os.path.join(get_directory_of_current_file(), "data", "read_test")
    file_binary = get_binary_from_file(test_file_path)
    assert file_binary == b'this is a test', "content not correct"
    # Test none existing file
    none_existing_file_path = os.path.join(get_directory_of_current_file(), "data", "none_existing_file")
    file_binary = get_binary_from_file(none_existing_file_path)
    assert file_binary == b'', "content not correct"
    # Test link
    link_path = os.path.join(get_directory_of_current_file(), "data", "link_test")
    file_binary = get_binary_from_file(link_path)
    assert file_binary == 'symbolic link -> read_test'


def test_fail_safe_read_file_string_list():
    test_file_path = os.path.join(get_directory_of_current_file(), "data", "multiline_test.txt")
    lines = get_string_list_from_file(test_file_path)
    assert lines == ['first line', 'second line', 'th\ufffdrd line', '', 'first line'], "lines not correct"


def test_fail_safe_write_file(tempdir):
    file_path = os.path.join(tempdir.name, "test_folder", "test_file")
    write_binary_to_file(b'this is a test', file_path)
    assert os.path.exists(file_path), "file not created"
    read_binary = get_binary_from_file(file_path)
    assert read_binary == b'this is a test', "written data not correct"
    # Test not overwrite flag
    write_binary_to_file(b'do not overwrite', file_path, overwrite=False)
    read_binary = get_binary_from_file(file_path)
    assert read_binary == b'this is a test', "written data not correct"
    # Test overwrite flag
    write_binary_to_file(b'overwrite', file_path, overwrite=True)
    read_binary = get_binary_from_file(file_path)
    assert read_binary == b'overwrite', "written data not correct"
    # Test copy_file_flag
    write_binary_to_file(b'second_overwrite', file_path, file_copy=True)
    assert os.path.exists("{}-1".format(file_path)), "new file copy does not exist"
    read_binary_original = get_binary_from_file(file_path)
    assert read_binary_original == b'overwrite', "original file no longer correct"
    read_binary_new = get_binary_from_file("{}-1".format(file_path))
    assert read_binary_new == b'second_overwrite', "binary of new file not correct"


def test_get_counted_file_path():
    assert _get_counted_file_path("/foo/bar") == "/foo/bar-1", "simple case"
    assert _get_counted_file_path("/foo/bar-11") == "/foo/bar-12", "simple count two digits"
    assert _get_counted_file_path("foo-34/bar") == "foo-34/bar-1", "complex case"


def test_delete_file(tempdir):
    file_path = os.path.join(tempdir.name, "test_folder", "test_file")
    write_binary_to_file(b'this is a test', file_path)
    assert os.path.exists(file_path), "file not created"
    delete_file(file_path)
    assert not os.path.exists(file_path)
    # Test delete none existing file
    delete_file(file_path)


def test_create_symlink(tempdir):
    test_file_path = os.path.join(tempdir.name, 'test_folder', 'test_file')
    symlink_path = os.path.join(tempdir.name, 'test_symlink')
    create_symlink(test_file_path, symlink_path)
    assert os.readlink(symlink_path) == test_file_path
    symlink_path_none_existing_dir = os.path.join(tempdir.name, 'some_dir/test_symlink')
    create_symlink(test_file_path, symlink_path_none_existing_dir)
    assert os.readlink(symlink_path_none_existing_dir) == test_file_path
    # check error handling
    create_symlink(test_file_path, symlink_path)


def test_get_safe_name():
    a = "/()=Hello%&World!? Foo"
    assert get_safe_name(a) == "HelloWorld_Foo", "result not correct"
    b = 250 * 'a'
    assert len(get_safe_name(b)) == 200, "lenght not cutted correctly"


def test_get_files_in_dir(create_symlinks):
    test_dir_path = os.path.join(get_directory_of_current_file(), "data")
    result = get_files_in_dir(test_dir_path)
    assert os.path.join(test_dir_path, "read_test") in result, "file in root folder not found"
    assert os.path.join(test_dir_path, "test_folder/generic_test_file") in result, "file in sub folder not found"
    assert len(result) == 6, "number of found files not correct"


def test_get_files_in_dir_error():
    result = get_files_in_dir("/none_existing/dir")
    assert result == [], "error result should be an empty list"


def test_get_dirs(tempdir):
    test_dirs = ["dir_1", "dir_2", "dir_1/sub_dir"]
    for item in test_dirs:
        os.mkdir(os.path.join(tempdir.name, item))
    result = get_dirs_in_dir(tempdir.name)
    expected_result = [os.path.join(tempdir.name, "dir_1"), os.path.join(tempdir.name, "dir_2")]
    assert sorted(result) == expected_result, "found dirs not correct"


def test_get_dirs_in_dir_error():
    result = get_dirs_in_dir("/none_existing/dir")
    assert result == [], "error result should be an empty list"


def test_get_dir_of_file_relative_path():
    relative_path_result = get_dir_of_file("test/some_file")
    expected_result = os.path.join(os.getcwd(), "test")
    assert relative_path_result == expected_result


def test_get_dir_of_file_absolute_path(tempdir):
    test_file_path = os.path.join(tempdir.name, 'test_file')
    write_binary_to_file('test', test_file_path)
    absolute_file_path_result = get_dir_of_file(test_file_path)
    assert absolute_file_path_result == tempdir.name


@pytest.mark.parametrize('symlinks, directories, expected_number', [
    (True, True, 7),
    (False, True, 5),
    (True, False, 5),
    (False, False, 3),
])
def test_safe_rglob(symlinks, directories, expected_number):
    test_dir_path = Path(get_directory_of_current_file()).parent / 'tests' / 'data'
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
