import os
import bitmath


def read_in_chunks(file_object, chunk_size=1024):
    '''
    Helper function to read large file objects iteratively in smaller chunks. Can be used like this::

        file_object = open('somelargefile.xyz', 'rb')
        for chunk in read_in_chunks(file_object):
            # Do something with chunk

    :param file_object: The file object from which the chunk data is read. Must be a subclass of ``io.BufferedReader``.
    :param chunk_size: Number of bytes to read per chunk.
    :type chunk_size: int
    :return: Returns a generator to iterate over all chunks, see above for usage.
    '''
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def get_directory_for_filename(filename):
    '''
    Convenience function which returns the absolute path to the directory that contains the given file name.

    :param filename: Path of the file. Can be absolute or relative to the current directory.
    :type filename: str
    :return: Absolute path of the directory
    '''
    return os.path.dirname(os.path.abspath(filename))


def create_dir_for_file(file_path):
    '''
    Creates all directories of file path. File path may include the file as well.

    :param file_path: Path of the file. Can be absolute or relative to the current directory.
    :type file_path: str
    :return: None
    '''
    directory = os.path.dirname(os.path.abspath(file_path))
    os.makedirs(directory, exist_ok=True)


def human_readable_file_size(size_in_bytes):
    '''
    Returns a nicly human readable file size

    :param size_in_bytes: Size in Bytes
    :type size_in_bytes: int
    :return: str
    '''
    return bitmath.Byte(bytes=size_in_bytes).best_prefix().format('{value:.2f} {unit}')
