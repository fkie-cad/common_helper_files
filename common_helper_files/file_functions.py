import io
from pathlib import Path
from typing import Type, Union

import bitmath


def read_in_chunks(file_object: Type[io.BufferedReader], chunk_size=1024) -> bytes:
    '''
    Helper function to read large file objects iteratively in smaller chunks. Can be used like this::

        file_object = open('somelargefile.xyz', 'rb')
        for chunk in read_in_chunks(file_object):
            # Do something with chunk

    :param file_object: The file object from which the chunk data is read. Must be a subclass of ``io.BufferedReader``.
    :param chunk_size: Number of bytes to read per chunk.
    :return: Returns a generator to iterate over all chunks, see above for usage.
    '''
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def get_directory_for_filename(filename: Union[str, Path]) -> str:
    '''
    Convenience function which returns the absolute path to the directory that contains the given file name.

    :param filename: Path of the file. Can be absolute or relative to the current directory.
    :return: Absolute path of the directory

    .. deprecated::
        You should use pathlib instead of this function.

    '''
    return str(Path(filename).resolve().parent)


def create_dir_for_file(file_path: Union[str, Path]) -> None:
    '''
    Creates all directories of file path. File path may include the file as well.

    :param file_path: Path of the file. Can be absolute or relative to the current directory.

    .. deprecated::
        You should use pathlib instead of this function.
    '''
    Path(file_path).resolve().parent.mkdir(parents=True, exist_ok=True)


def human_readable_file_size(size_in_bytes: int) -> str:
    '''
    Returns a nicly human readable file size

    :param size_in_bytes: Size in Bytes
    '''
    return bitmath.Byte(bytes=size_in_bytes).best_prefix().format('{value:.2f} {unit}')
