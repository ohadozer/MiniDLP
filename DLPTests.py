import unittest

from Authenticators import WebAuthenticator
from DriveClient import DriveClient


class TestDriveClient(unittest.TestCase):

    """
    some unit-test for the Drive client class
    """

    def setUp(self):
        authenticator = WebAuthenticator()
        auth_object = authenticator.authenticate()
        self.drive_client = DriveClient(auth_object)

    def tearDown(self):
        pass

    def test_file_metadata(self):

        title, content = self.drive_client.get_content('1NFo9gAVHqJCug2k9IlKVKA8DBE_z20yx')
        self.assertEqual(title, 'just_a_text_file.txt')
        self.assertIn('Rebuild Python and reinstall', content)

        title, _ = self.drive_client.get_content('1toHDRsSxUcFqVG8v_Q9uARE45aXPz4Rk')
        self.assertEqual(title, 'ibans_001.txt')


if __name__ == '__main__':
    unittest.main()
