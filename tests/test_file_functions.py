import unittest
from common_helper_files import human_readable_file_size


class Test_file_functions(unittest.TestCase):

    def test_human_readable_file_size(self):
        self.assertEqual(human_readable_file_size(1024), '1.00 KiB')
        self.assertEqual(human_readable_file_size(5000), '4.88 KiB')
