import unittest

from securityclientpy.version import __version__

class TestVideoStreamer(unittest.TestCase):
    """set of test for version.__version"""

    def test_version(self):
        app_version = __version__
        self.assertIsNotNone(app_version)
