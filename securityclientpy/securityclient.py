# -*- coding: utf-8 -*-
#
# logic for establing server communication, processing data, and sending data to clients
#

import requests
import time
from flask import Flask, jsonify
from threading import Thread

from securityclientpy import _logger
from securityclientpy.hwcontroller import HardwareController
from securityclientpy.videostreamer import VideoStreamer

_SUCCESS_CODE = 201
_FAILURE_CODE = 404

app = Flask(__name__)

class SecurityClient(object):
    """ Todo: add class description here
    """

    # Constants
    _DEFAULT_CAMERA_ID = 0
    _GEOIP_HOSTNAME = "http://freegeoip.net/json"

    # status LED flash signals
    _FLASH_NEW_DEVICE = 3
    _FLASH_SYSTEM_ARMED = 10
    _FLASH_SYSTEM_DISARMED = 5
    _FLASH_DEVICE_CONNECTED = 4
    _FLASH_SERVER_ON = 3

    def __init__(self, host, port, no_hardware=False, no_video=False, testing=False):
        """constructor method for SecurityServer

        HardwareController: used to control all pieces of hardware connected to the raspberry pi
        DeviceManager: module used to store device information that connects to the server
        SecurityConfig: a collection of security attributes about the system (system armed, cameras live, etc.)
        VideoStreamer: module to control video streaming to clients from server, and motion detection

        We use the 2 config values (no_hardware and no_video) for different development modes
        """
        self.host = host
        self.port = port

        self.no_hardware = no_hardware
        self.no_video = no_video

        # Set up different configs if needed
        if not self.no_hardware:
            self.hwcontroller = HardwareController()
        if not self.no_video:
            self.videostream = VideoStreamer(SecurityServer._DEFAULT_CAMERA_ID)

        # Use inner methods so API methods can access self parameter

        # Error handling
        @app.errorhandler(_FAILURE_CODE)
        def not_found(error):
            return jsonify({'code': _FAILURE_CODE,'data': 0})

        @app.route('/system/arm', methods=['GET'])
        def arm_system():
            """API route to arm the security system"""
            pass

        @app.route('/system/disarm', methods=['GET'])
        def disarm_system():
            """API route to disarm the security system"""
            pass

        @app.route('/system/false_alarm', methods=['GET'])
        def set_false_alarm():
            """API route to set security breach as false alarm"""
            pass

        @app.route('/system/location', methods=['GET'])
        def get_gps_location():
            """API route to get gps location coordinates"""
            pass

        @app.route('/system/temperature', methods=['GET'])
        def get_temperature():
            """API route to get current temperature data"""
            pass

    def _system_armed_thread(self):
        """starts once the system has been armed

        Before starting this thread, we can safely assume that the `system_armed` config attribute has been set to
        True. That means, in this method, we can loop until that value has been set to false. It will only be set to
        false if a client sends data to the server to do so (Hence, disarming the system).

        In this process, the things we want to do are:
            • Read from the camera, getting the status and motion detected values from it.
            • If we have successfully read from the camera and motion has been detected, someone has either broken
                into the car, or its a false alarm (Kids are playing on the back seat) :)
            • To be on the safe side, we assume its a break in, and fire up the `system_breached_thread`
            • If motion hasnt been detected, we just continue to check until the system is disarmed
        """
        _logger.debug('System armed in 5 secs.')
        time.sleep(5)
        while self.security_config.system_armed:
            if not self.no_hardware and not self.no_video:
                motion_detected = self.hwcontroller.read_motion_sensor()
                noise_detected = self.hwcontroller.read_noise_sensor()
                if motion_detected or noise_detected:
                    self.security_config.system_breached = True
                    self.hwcontroller.status_led_flash_start()
                    system_breach_thread = Thread(target=self._system_breached_thread)
                    system_breach_thread.start()
            time.sleep(0.2)

    def _system_breached_thread(self):
        """starts once the system has been breached

        This method is fired as a separate thread once the system is armed and motion or loud sound has been detected.

        In this process, we want to:
            • Initialize video writer object to record video to, and save the files on the server.
                - Video files are saved with the following format: system-breach-stream1-{:%Y-%m-%d %-I:%M %p}.avi
                - Using this format, we can easily operate on filenames to access files from particular dates and
                    times as we please.
            • While the `system_breached` security setting is set to True, update the video files with more frames.
            • While this is happeneing, the `security_thread` will still be up, and the client can easily look at
                the live stream while we are recording video.
            • The thread will stop once we either recieve false alarm data from the client, or they reach out to dispatchers
                and the situation is resolved.
        """
        _logger.debug('System breached.')
        self.logs.add_log("System breached", SecurityServer._SECURITY_CONTROLLED_LOG_TYPE)
        # video recorder
        fourcc = cv2.cv.CV_FOURCC(*'XVID')  # cv2.VideoWriter_fourcc() does not exist
        video_writer = cv2.VideoWriter("system-breach-recording-{:%b %d, %Y %-I:%M %p}.avi".format(datetime.datetime().now()),
                                       fourcc, 20, (680, 480))
        while self.security_config.system_breached:
            if not self.no_hardware:
                status, frame_jpeg, frame = self.videostream.read()
                if status:
                    video_writer.write(frame)

    def save_settings(self):
        """method is fired when the user disconnects or the socket connection is broken"""
        _logger.debug('Saving security session.')

        if not self.no_video or not self.no_hardware:
            self.videostream.release_stream()

    def start(self):
        """starts the flask app"""
        app.run(host=self.host, port=self.port)

    def server_app(self):
        return app

    def _fetch_location_coordinates(self):
        """fetches the location coordinates of the system, using the freegeoip/ host

        returns:
            dict -> {'latitude': float, 'longitude': float}
        """
        geo = requests.get(self._GEOIP_HOSTNAME)
        json_data = geo.json()
        position = {
            "latitude": float(json_data["latitude"]),
            "longitude": float(json_data["longitude"])
        }
        return position
