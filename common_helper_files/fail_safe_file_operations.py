import logging
import os
import re
import sys
from builtins import FileExistsError

from .file_functions import create_dir_for_file


def get_binary_from_file(file_path):
    """
    Fail-safe file read operation. Symbolic links are converted to text files including the link.
    Errors are logged. No exception raised.

    :param file_path: Path of the file. Can be absolute or relative to the current directory.
    :type file_path: str
    :return: file's binary as bytes; returns empty byte string on error
    """
    try:
        if os.path.islink(file_path):
            binary = "symbolic link -> {}".format(os.readlink(file_path))
        else:
            with open(file_path, 'rb') as f:
                binary = f.read()
    except Exception as e:
        logging.error("Could not read file: {} {}".format(sys.exc_info()[0].__name__, e))
        binary = b''
    return binary


def get_string_list_from_file(file_path):
    """
    Fail-safe file read operation returning a list of text strings.
    Errors are logged. No exception raised.

    :param file_path: Path of the file. Can be absolute or relative to the current directory.
    :type file_path: str
    :return: file's content as text string list; returns empty list on error
    """
    try:
        raw = get_binary_from_file(file_path)
        string = raw.decode(encoding='utf_8', errors='replace')
        return string.split("\n")
    except Exception as e:
        logging.error("Could not read file: {} {}".format(sys.exc_info()[0].__name__, e))
        return []


def write_binary_to_file(file_binary, file_path, overwrite=False, file_copy=False):
    """
    Fail-safe file write operation. Creates directories if needed.
    Errors are logged. No exception raised.

    :param file_binary: binary to write into the file
    :type file_binary: bytes or str
    :param file_path: Path of the file. Can be absolute or relative to the current directory.
    :type file_path: str
    :param overwrite: overwrite file if it exists
    :type overwrite: bool
    :default overwrite: False
    :param file_copy: If overwrite is false and file already exists, write into new file and add a counter to the file name.
    :type file_copy: bool
    :default file_copy: False
    :return: None
    """
    try:
        create_dir_for_file(file_path)
        if not os.path.exists(file_path) or overwrite:
            _write_file(file_path, file_binary)
        elif file_copy and not overwrite:
            new_path = _get_counted_file_path(file_path)
            _write_file(new_path, file_binary)
    except Exception as e:
        logging.error("Could not write file: {} {}".format(sys.exc_info()[0].__name__, e))


def _write_file(file_path, binary):
    with open(file_path, 'wb') as f:
        f.write(binary)


def _get_counted_file_path(original_path):
    tmp = re.search(r"-([0-9]+)\Z", original_path)
    if tmp is not None:
        current_count = int(tmp.group(1))
        new_file_path = re.sub(r"-[0-9]+\Z", "-{}".format(current_count+1), original_path)
    else:
        new_file_path = "{}-1".format(original_path)
    return new_file_path


def delete_file(file_path):
    """
    Fail-safe delete file operation. Deletes a file if it exists.
    Errors are logged. No exception raised.

    :param file_path: Path of the file. Can be absolute or relative to the current directory.
    :type file_path: str
    :return: None
    """
    try:
        os.unlink(file_path)
    except Exception as e:
        logging.error("Could not delete file: {} {}".format(sys.exc_info()[0].__name__, e))


def create_symlink(src_path, dst_path):
    """
    Fail-safe symlink operation. Symlinks a file if dest does not exist.
    Errors are logged. No exception raised.

    :param src_path: src file
    :type src_path: str
    :param dst_path: link location
    :type dst_path: str
    :return: None
    """
    try:
        create_dir_for_file(dst_path)
        os.symlink(src_path, dst_path)
    except FileExistsError as e:
        logging.debug("Could not create Link: File exists: {}".format(e))
    except Exception as e:
        logging.error("Could not create link: {} {}".format(sys.exc_info()[0].__name__, e))


def get_safe_name(file_name, max_size=200, valid_characters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_+. '):
    """
    removes all problematic characters from a file name
    cuts file names if they are too long

    :param file_name: Original file name
    :type file_name: str
    :param max_size: maximum allowed file name length
    :type max_size: int
    :default max_size: 200
    :param valid_characters: characters that shall be allowed in a file name
    :type valid_characters: str
    :default valid_characters: 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_+. '
    :return: str
    """
    allowed_charachters = set(valid_characters)
    safe_name = filter(lambda x: x in allowed_charachters, file_name)
    safe_name = "".join(safe_name)
    safe_name = safe_name.replace(" ", "_")
    if len(safe_name) > max_size:
        safe_name = safe_name[0:max_size]
    return safe_name


def get_files_in_dir(directory_path):
    """
    Returns a list with the absolute paths of all files in the directory directory_path

    :param directory_path: directory including files
    :type directory_path: str
    :return: list
    """
    result = []
    try:
        for file_path, _, files in os.walk(directory_path):
            for file_ in files:
                result.append(os.path.abspath(os.path.join(file_path, file_)))
    except Exception as e:
        logging.error("Could not get files: {} {}".format(sys.exc_info()[0].__name__, e))
    return result


def get_dirs_in_dir(directory_path):
    """
    Returns a list with the absolute paths of all 1st level sub-directories in the directory directory_path.

    :param directory_path: directory including sub-directories
    :type directory_path: str
    :return: list
    """
    result = []
    try:
        dir_content = os.listdir(directory_path)
        for item in dir_content:
            dir_path = os.path.join(directory_path, item)
            if os.path.isdir(dir_path):
                result.append(dir_path)
    except Exception as e:
        logging.error("Could not get directories: {} {}".format(sys.exc_info()[0].__name__, e))
    return result


def get_dir_of_file(file_path):
    """
    Returns absolute path of the directory including file

    :param file_path: Paht of the file
    :type: paht-like object
    :return: string
    """
    try:
        return os.path.dirname(os.path.abspath(file_path))
    except Exception as e:
        logging.error("Could not get directory path: {} {}".format(sys.exc_info()[0].__name__, e))
        return "/"
