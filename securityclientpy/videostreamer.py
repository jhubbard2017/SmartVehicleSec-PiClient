# -*- coding: utf-8 -*-
#
# module for retrieving camera stream bytes to send from server to clients
#

import cv2

from securityclientpy import _logger


class VideoStreamer(object):
    """manages and controls camera stream data"""

    _STREAM_MIN_AREA = 500

    def __init__(self, camera, no_video):
        """set the video object from the camera number

        Default camera # is 0. This simply enables usb camera to be used by openCV
        """
        self._camera = camera
        self._no_video = no_video
        self._stream = None

        if not self._no_video:
            self._stream = cv2.VideoCapture(self._camera)

    def release_stream(self):
        if not self._no_video:
            self._stream.release()

    def get_frame(self):
        """reads a frame from the camera stream and converts it to bytes to send

        returns:
            bytes
        """
        if not self._no_video:
            success, image = self._stream.read()
            return success, image
        return None, None

    @property
    def camera(self):
        return self._camera

    @property
    def no_video(self):
        return self._no_video

    @property
    def stream(self):
        return self._stream != None
