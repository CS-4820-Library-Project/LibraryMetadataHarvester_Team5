import unittest
import subprocess
import os

class TestLMHInterface(unittest.TestCase):

    def setUp(self):
        print('\nsetUp')

    def tearDown(self):
        print('\ntearDown')

    def test_basic_functionality_isbn(self):
        result = subprocess.run(['python', 'lmh.py', '-i', 'test_data/metadata_sample_isbns.txt', '-o', 'output.tsv', '--retrieve-ocns'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue("9780191513015" in result.stdout)
        # self.assertTrue("Retrieved OCNs: ['000000000', '000000000']" in result.stdout)

    def test_basic_functionality_ocn(self):
        result = subprocess.run(['python', 'lmh.py', '-i', 'test_data/sample_metadata_ocns.txt', '-o', 'output.tsv', '--retrieve-isbns'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue("922903415" in result.stdout)
        # self.assertTrue("Retrieved ISBNs: ['0000000000000', '0000000000000']" in result.stdout)

    def test_output_file_handling(self):
        result = subprocess.run(['python', 'lmh.py', '-i', 'test_data/metadata_sample_isbns.txt', '--retrieve-ocns'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        # self.assertTrue("Retrieved OCNs: ['000000000', '000000000']" in result.stdout)
        # self.assertTrue(os.path.exists('output.tsv'))  # Check if output file is generated

if __name__ == '__main__':
    unittest.main()