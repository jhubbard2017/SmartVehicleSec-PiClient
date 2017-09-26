# -*- coding: utf-8 -*-
#
# logic for establing server communication, processing data, and sending data to clients
#

import requests
import time
from flask import Flask, jsonify, request
from threading import Thread

from securityclientpy import _logger
from securityclientpy.get_device_id import get_mac_address
from securityclientpy.hwcontroller import HardwareController
from securityclientpy.videostreamer import VideoStreamer
from securityclientpy.speed_limit import SpeedLimit
from securityclientpy.flask_error_handling import FlaskErrorHandling

_SUCCESS_CODE = 201
_FAILURE_CODE = 404

app = Flask(__name__)

class SecurityClient(object):

    # Constants
    _DEFAULT_CAMERA_ID = 0
    _GEOIP_HOSTNAME = "http://freegeoip.net/json"
    _TEMPERATURE_LIMIT = 85.0

    # status LED Constants
    _FLASH_NEW_DEVICE = 3
    _FLASH_SYSTEM_ARMED = 10
    _FLASH_SYSTEM_DISARMED = 5
    _FLASH_DEVICE_CONNECTED = 4
    _FLASH_SERVER_ON = 3

    # Error message keys
    _DEVICE_KEY = 'rd_mac_address'
    _ARM_SYSTEM_KEY = 'arm_system'
    _DISARM_SYSTEM_KEY = 'disarm_system'
    _FALSE_ALARM_KEY = 'false_alarm'

    def __init__(self, host, port, serverhost, serverport, no_hardware=False, no_video=False, dev=False, testing=False):
        """constructor method for SecurityServer"""

        # Connection parameters for flask app
        self.host = host
        self.port = port

        # Use to connect and send http requests to server
        self.serverhost = serverhost
        self.serverport = serverport

        # configs for different development modes
        self.no_hardware = no_hardware
        self.no_video = no_video

        # Set up necessary objects for associated configs
        if not self.no_hardware:
            self.hwcontroller = HardwareController()
            self.speed_limit_checker = SpeedLimit(self.serverhost, self.serverport, self.mac_address)

        if not self.no_video:
            self.videostream = VideoStreamer(SecurityServer._DEFAULT_CAMERA_ID)

        # If in development mode, we set a MAC address "DEVELOP" to easily access it from the server
        # If testing, we set a MAC address "TESTING"
        if dev:
            self.mac_address = 'DEVELOP'
        else:
            self.mac_address = get_mac_address()
        if testing:
            self.mac_address = 'TESTING'

        # Initialize local copy of security config values
        self.system_armed = False
        self.system_breached = False

        # Setup system on the server
        self._initialize_client()
        self.error_handling = FlaskErrorHandling(self.mac_address)

        #
        # We use inner methods for the flask api route methods so that they can access the self pointer
        # of this class.
        #

        @app.route('/system/arm', methods=['POST'])
        def arm_system():
            """API route to arm the security system

            required data:
                rd_mac_address: str
            """
            error_found, error_message = self.error_handling.check_system_request(
                request.json, config_key=SecurityClient._ARM_SYSTEM_KEY, config_value=self.system_armed
            )
            if error_found:
                return self.abort_with_message(error_message)

            self.system_armed = True
            thread = Thread(target=self._system_armed_thread)
            thread.start()
            return jsonify({'code': _SUCCESS_CODE,'data': True})

        @app.route('/system/disarm', methods=['POST'])
        def disarm_system():
            """API route to disarm the security system

            required data:
                rd_mac_address: str
            """
            error_found, error_message = self.error_handling.check_system_request(
                request.json, config_key=SecurityClient._DISARM_SYSTEM_KEY, config_value=(not self.system_armed)
            )
            if error_found:
                return self.abort_with_message(error_message)

            self.system_armed = False
            return jsonify({'code': _SUCCESS_CODE,'data': True})

        @app.route('/system/false_alarm', methods=['POST'])
        def set_false_alarm():
            """API route to set security breach as false alarm

            required data:
                rd_mac_address: str
            """
            error_found, error_message = self.error_handling.check_system_request(
                request.json, config_key=SecurityClient._FALSE_ALARM_KEY, config_value=self.system_breached
            )
            if error_found:
                return self.abort_with_message(error_message)

            self.system_breached = False
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/location', methods=['POST'])
        def get_gps_location():
            """API route to get gps location coordinates

            required data:
                rd_mac_address: str
            """
            error_found, error_message = self.error_handling.check_system_request(request.json)
            if error_found:
                return self.abort_with_message(error_message)

            data = self._fetch_location_coordinates()
            if not data:
                error_message = 'Failed to get GPS data'
                return self.abort_with_message(error_message)

            _logger.info('Sending gps coordinates.')
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

        @app.route('/system/temperature', methods=['POST'])
        def get_temperature():
            """API route to get current temperature data

            required data:
                rd_mac_address: str
            """
            error_found, error_message = self.error_handling.check_system_request(request.json)
            if error_found:
                return self.abort_with_message(error_message)

            if not self.no_hardware:
                data = self.hwcontroller.read_thermal_sensor()
            else:
                data = {'fahrenheit': 73.3, 'celcius': 32.0}

            _logger.info('Sending temperature')
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

        @app.route('/system/speedometer', methods=['POST'])
        def get_speedometer_data():
            """API route to get speedometer data

            required data:
                rd_mac_address: str
            """
            error_found, error_message = self.error_handling.check_system_request(request.json)
            if error_found:
                return self.abort_with_message(error_message)

            if not self.no_hardware:
                data = self.hwcontroller.read_speedometer_sensor()
            else:
                data = {'speed': 75, 'altitude': 1024.6, 'heading': 120, 'climb': 117}

            _logger.info('Sending speedometer data')
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

    def abort_with_message(self, error):
        """error handling method for FLASK API calls

        args:
            message: str

        returns:
            jsonify()
        """
        _logger.info('Aborting with error: [{0}]'.format(message))
        return jsonify({'code': _FAILURE_CODE, 'data': False, 'message': error})

    def _initialize_client(self):
        """update ip address and port number on server database, and any other data that needs to be stored

        Also in this method, we want to get the current security config of the system
            - If we are updating connection parameters, the security config should already be created
            - If we are adding a new connection, we need to create the new security config and initialize both config
                values to false
        """
        connection_exist = self.get_connection_on_server()
        if connection_exist == None:
            _logger.info('Error getting connection information')
            return

        if connection_exist:
            success = self.update_connection_on_server()
            if not success:
                _logger.info('Failed to update connection on server')
                return
            success = self.update_security_config()
            if not success:
                _logger.info('Failed to get security config from server')
                return
        else:
            success = self.add_connection_on_server()
            if not success:
                _logger.info('Failed to add connection on server')
                return
            success = self.create_security_config_on_server()
            if not success:
                _logger.info('Failed to create security config on server')
                return

        _logger.info('Successfully initialized system')

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
        _logger.info('System will arm in 5 secs')
        time.sleep(5)
        _logger.info('System armed')
        motion_already_detected = self._check_motion_detection()
        if motion_already_detected:
            self.thread_for_motion_already_detected()
        else:
            self.thread_for_motion_not_already_detected()

    def thread_for_motion_already_detected(self):
        """method that runs if motion is already detected"""
        while self.system_armed:
            if not self.no_hardware and not self.no_video:
                shock_detected = self.hwcontroller.read_shock_sensor()
                temp = self.hwcontroller.read_thermal_sensor()
                if shock_detected or temp['fahrenheit'] >= 85.0:
                    self.system_breached = True
                    self.hwcontroller.status_led_flash_start()
                    system_breach_thread = Thread(target=self._system_breached_thread)
                    system_breach_thread.start()

                    if temp['fahrenheit'] >= SecurityClient._TEMPERATURE_LIMIT:
                        # Todo: send motification to mobile app
                        pass
        _logger.info('System disarmed')

    def thread_for_motion_not_already_detected(self):
        """method that runs if motion is not already detected at the start of arming the system"""
        while self.system_armed:
            if not self.no_hardware and not self.no_video:
                motion_detected = self.hwcontroller.read_motion_sensor()
                noise_detected = self.hwcontroller.read_noise_sensor()
                shock_detected = self.hwcontroller.read_shock_sensor()
                if motion_detected or noise_detected or shock_detected:
                    self.system_breached = True
                    self.hwcontroller.status_led_flash_start()
                    system_breach_thread = Thread(target=self._system_breached_thread)
                    system_breach_thread.start()
        _logger.info('System disarmed')

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
        _logger.info('System breached.')
        # Todo: Notify server
        # video recorder
        fourcc = cv2.cv.CV_FOURCC(*'XVID')  # cv2.VideoWriter_fourcc() does not exist
        video_writer = cv2.VideoWriter("system-breach-recording-{:%b %d, %Y %-I:%M %p}.avi".format(datetime.datetime().now()),
                                       fourcc, 20, (680, 480))
        while self.system_breached:
            if not self.no_hardware:
                status, frame_jpeg, frame = self.videostream.read()
                if status:
                    video_writer.write(frame)
        _logger.info('System breach ended')

    def save_settings(self):
        """method is fired when the user disconnects or the socket connection is broken"""
        _logger.info('Saving security session.')

        if not self.no_video:
            self.videostream.release_stream()
        if not self.no_hardware:
            self.speed_limit_checker.stop_thread()

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
        if not self.no_hardware:
            position = self.hwcontroller.read_gps_sensor()
        else:
            geo = requests.get(self._GEOIP_HOSTNAME)
            json_data = geo.json()
            position = {
                "latitude": float(json_data["latitude"]),
                "longitude": float(json_data["longitude"])
            }

        return position

    def send_request_to_server(self, path, data):
        """method to send request to server and get the response

        args:
            url: str
            data: {}

        returns:
            {}
        """
        url = 'http://{0}:{1}/system/{2}'.format(self.serverhost, self.serverport, path)
        data = {'rd_mac_address': self.mac_address}
        for key, value in data.iteritems():
            data[key] = value
        response = requests.post(url, json=data)
        if not response.json():
            return None

        return response.json()

    def update_connection_on_server(self):
        """method to send server request for updating connection on the server"""
        success = True
        path = 'update_connection'
        data = {'ip_address': self.host, 'port': self.port}
        response = self.send_request_to_server(path, data)
        if not response['data']:
            _logger.info('Failed to update connection on server')
            return not success

        return success

    def add_connection_on_server(self):
        """method to send server request for adding connection on the server"""
        success = True
        path = 'add_connection'
        data = {'ip_address': self.host, 'port': self.port}
        response = self.send_request_to_server(path, data)
        if not response['data']:
            _logger.info('Failed to add connection on server')
            return not success

        return success

    def update_security_config(self):
        """method to send server request for updating local security config with that which is on the server"""
        success = True
        path = 'security_config'
        response = self.send_request_to_server(path, data)
        if not response['data']:
            return not success

        config = response['data']
        self.system_armed = config['system_armed']
        self.system_breached = config['system_breached']
        return success

    def create_security_config_on_server(self):
        """method to send server request for creating a new security config"""
        success = True
        # Create new security config for this device on server
        path = 'create_securityconfig'
        response = self.send_request_to_server(path, data)
        if not response['data']:
            _logger.info('Failed to create security config on server')
            return not success

        return success

    def get_connection_on_server(self):
        """method to send server request for checking if connection exist on server"""
        success = True
        path = 'get_connection'
        response = requests.post(url, json=data)
        if response['code'] == _FAILURE_CODE:
            _logger.info('Failure code: [{0}]'.format(json_data['message']))
            return None

        if not response['data']:
            return not success

        return success

    def _check_motion_detection(self):
        """checks if motion is detected for a time of 5 seconds before arming system

        returns:
            bool
        """
        motion_detected = False
        if not self.no_hardware:
            for x in range(5):
                motion_detected = self.hwcontroller.read_motion_sensor()
                time.sleep(1)
                if motion_detected:
                    break

        return motion_detected