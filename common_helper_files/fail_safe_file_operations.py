import logging
import os
import re
import sys
from pathlib import Path
from typing import Iterable, List, Union

from .file_functions import create_dir_for_file


def get_binary_from_file(file_path: Union[str, Path]) -> Union[str, bytes]:
    '''
    Fail-safe file read operation. Symbolic links are converted to text files including the link.
    Errors are logged. No exception raised.

    :param file_path: Path of the file. Can be absolute or relative to the current directory.
    :return: file's binary as bytes; returns empty byte string on error
    '''
    try:
        path = Path(file_path)
        if path.is_symlink():
            # We need to wait for python 3.9 for Path.readlink
            binary = f'symbolic link -> {os.readlink(path)}'
        else:
            binary = path.read_bytes()
    except Exception as e:
        logging.error(f'Could not read file: {e}', exc_info=True)
        binary = b''

    return binary


def get_string_list_from_file(file_path: Union[str, Path]) -> List[str]:
    '''
    Fail-safe file read operation returning a list of text strings.
    Errors are logged. No exception raised.

    :param file_path: Path of the file. Can be absolute or relative to the current directory.
    :return: file's content as text string list; returns empty list on error
    '''
    raw = get_binary_from_file(file_path)
    raw_string = raw.decode(encoding='utf-8', errors='replace')
    cleaned_string = raw_string.replace('\r', '')
    return cleaned_string.split('\n')


def write_binary_to_file(file_binary: Union[str, bytes], file_path: Union[str, Path], overwrite: bool = False, file_copy: bool = False) -> None:
    '''
    Fail-safe file write operation. Creates directories if needed.
    Does not overwrite existing files if ``overwrite`` is not set.
    Errors are logged.
    Raises a ``ValueError`` if ``overwrite`` and ``file_copy`` are both ``True``.

    :param file_binary: binary to write into the file
    :param file_path_str: Path of the file. Can be absolute or relative to the current directory.
    :param overwrite: overwrite file if it exists
    :default overwrite: False
    :param file_copy: If overwrite is false and file already exists, write into new file and add a counter to the file name.
    :default file_copy: False
    '''
    if overwrite and file_copy:
        raise ValueError("The arguments overwrite and file_copy cannot both be true.")

    try:
        file_path = Path(file_path)
        if file_path.exists():
            if overwrite:
                file_path.write_bytes(file_binary)
            elif file_copy:
                file_path = Path(_get_counted_file_path(str(file_path)))
                file_path.write_bytes(file_binary)
        else:
            create_dir_for_file(file_path)
            file_path.write_bytes(file_binary)
    except Exception as exc:
        logging.error(f'Could not write file: {exc}', exc_info=True)


def _get_counted_file_path(original_path):
    tmp = re.search(r'-([0-9]+)\Z', original_path)
    if tmp is not None:
        current_count = int(tmp.group(1))
        new_file_path = re.sub(r'-[0-9]+\Z', '-{}'.format(current_count + 1), original_path)
    else:
        new_file_path = '{}-1'.format(original_path)
    return new_file_path


def delete_file(file_path: Union[str, Path]) -> None:
    '''
    Fail-safe delete file operation. Deletes a file if it exists.
    Errors are logged. No exception raised.

    :param file_path: Path of the file. Can be absolute or relative to the current directory.
    '''
    try:
        Path(file_path).unlink()
    except Exception as exc:
        logging.error(f'Could not delete file: {exc}', exc_info=True)


def create_symlink(src_path: Union[str, Path], dst_path: Union[str, Path]) -> None:
    '''
    Fail-safe symlink operation. Symlinks a file if dest does not exist.
    Errors are logged. No exception raised.

    :param src_path: src file
    :param dst_path: link location
    '''
    try:
        create_dir_for_file(dst_path)
        Path(dst_path).symlink_to(src_path)
    except FileExistsError as exc:
        logging.debug(f'Could not create Link: File exists: {exc}')
    except Exception as exc:
        logging.error(f'Could not create link: {exc}', exc_info=True)


def get_safe_name(file_name: str, max_size: int = 200, valid_characters: str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_+. ') -> str:
    '''
    removes all problematic characters from a file name
    cuts file names if they are too long

    :param file_name: Original file name
    :param max_size: maximum allowed file name length
    :default max_size: 200
    :param valid_characters: characters that shall be allowed in a file name
    :default valid_characters: 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_+. '
    '''
    allowed_charachters = set(valid_characters)
    safe_name = filter(lambda x: x in allowed_charachters, file_name)
    safe_name = ''.join(safe_name)
    safe_name = safe_name.replace(' ', '_')
    if len(safe_name) > max_size:
        safe_name = safe_name[0:max_size]
    return safe_name


def get_files_in_dir(directory_path: Union[str, Path]) -> List[str]:
    '''
    Returns a list with the absolute paths of all files in the directory directory_path

    :param directory_path: directory including files
    '''
    result = []
    try:
        for file_path, _, files in os.walk(directory_path):
            for file_ in files:
                result.append(str(Path(file_path, file_).absolute()))
    except Exception as exc:
        logging.error(f'Could not get files: {exc}', exc_info=True)
    return result


def get_dirs_in_dir(directory_path: Union[str, Path]) -> List[str]:
    '''
    Returns a list with the absolute paths of all 1st level sub-directories in the directory directory_path.

    :param directory_path: directory including sub-directories
    '''
    result = []
    try:
        path = Path(directory_path)
        for item in path.iterdir():
            if Path(item).is_dir():
                result.append(str(item.resolve()))
    except Exception as exc:
        logging.error(f'Could not get directories: {exc}', exc_info=True)

    return result


def get_dir_of_file(file_path: Union[str, Path]) -> str:
    '''
    Returns absolute path of the directory including file

    :param file_path: Path of the file

    .. deprecated::
        You should use pathlib instead of this function.
    '''
    try:
        return str(Path(file_path).resolve().parent)
    except Exception as exc:
        logging.error(f'Could not get directory path: {exc}', exc_info=True)
        return '/'


def safe_rglob(path: Path, include_symlinks: bool = True, include_directories: bool = True) -> Iterable[Path]:
    '''
    alternative to pathlib.rglob which tries to follow symlinks and crashes if it encounters certain broken ones
    '''
    if not path.is_symlink() and path.is_dir():
        for child_path in path.iterdir():
            yield from _iterate_path_recursively(child_path, include_symlinks, include_directories)
    else:
        yield from []


def _iterate_path_recursively(path: Path, include_symlinks: bool = True, include_directories: bool = True):
    try:
        if path.is_symlink():
            if include_symlinks and (path.is_file() or path.is_dir()):
                yield path
        elif path.is_file():
            yield path
        elif path.is_dir():
            if include_directories:
                yield path
            for child_path in path.iterdir():
                yield from _iterate_path_recursively(child_path, include_symlinks, include_directories)
    except PermissionError:
        logging.error(f'Permission Error: could not access path {path.absolute()}')
    except OSError:
        logging.warning(f'possible broken symlink: {path.absolute()}')
    yield from []
