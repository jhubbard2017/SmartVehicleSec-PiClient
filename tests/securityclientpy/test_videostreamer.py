import unittest

from securityclientpy.videostreamer import VideoStreamer


class TestVideoStreamer(unittest.TestCase):
    """set of test for videostreamer.VideoStreamer"""

    def setUp(self):
        self.camera = 0
        self.videostreamer = VideoStreamer(self.camera, no_video=False)

    def tearDown(self):
        self.videostreamer.release_stream()

    def test_no_video_config(self):
        vs = VideoStreamer(0, no_video=True)
        self.assertEqual(vs.camera, 0)
        self.assertTrue(vs.no_video)
        self.assertFalse(vs.stream)

        status, frame = vs.get_frame()
        self.assertIsNone(status)
        self.assertIsNone(frame)

    def test_with_video_config(self):
        vs = VideoStreamer(0, no_video=False)
        self.assertEqual(vs.camera, 0)
        self.assertFalse(vs.no_video)
        self.assertTrue(vs.stream)

        status, frame = vs.get_frame()
        self.assertIsNotNone(status)
        self.assertIsNotNone(frame)

    def test_get_frame(self):
        status, image = self.videostreamer.get_frame()
        self.assertTrue(status)
        self.assertIsNotNone(image)

    def test_not_camera(self):
        videostreamer = VideoStreamer(12, no_video=True)
        status, image = videostreamer.get_frame()
        self.assertFalse(status)
        self.assertIsNone(image)
