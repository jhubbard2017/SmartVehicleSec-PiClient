# -*- coding: utf-8 -*-
#
# module for handling rest api calls from clients
#

from flask import Flask
from flask import jsonify
from flask import request

from securityclientpy import _logger
from securityclientpy.Flask.error_handling import APIErrorHandling
from securityclientpy.threads import SecurityThreads

app = Flask(__name__)

class RestAPI(object):
    """Module for controlling rest api calls and methods"""

    # Constants
    _SUCCESS_CODE = 201
    _FAILURE_CODE = 404

    # Error message keys
    _DEVICE_KEY = 'rd_mac_address'
    _ARM_SYSTEM_KEY = 'arm_system'
    _DISARM_SYSTEM_KEY = 'disarm_system'
    _FALSE_ALARM_KEY = 'false_alarm'

    def __init__(self, host, port, serverhost, serverport, no_hardware, no_video, device_id):
        """Constructor method"""

        self.host = host
        self.port = port

        self.security_threads = SecurityThreads(serverhost, serverport, no_hardware, no_video, device_id)
        self.error_handling = APIErrorHandling(device_id)

        # We use inner methods for the flask api route methods so that they can access the self pointer
        # of this class.

        @app.route('/system/arm', methods=['POST'])
        def arm_system():
            """API route to arm the security system

            required data:
                rd_mac_address: str
            """
            status, error = self.error_handling.check_system_request(
                request.json, config_key=SecurityClient._ARM_SYSTEM_KEY, config_value=self.security_threads.system_armed
            )
            if not status: return self.abort_with_message(error)

            # Arm system
            self.security_threads.arm_system()
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/disarm', methods=['POST'])
        def disarm_system():
            """API route to disarm the security system

            required data:
                rd_mac_address: str
            """
            status, error = self.error_handling.check_system_request(
                request.json, config_key=SecurityClient._DISARM_SYSTEM_KEY, config_value=(not self.security_threads.system_armed)
            )
            if not status: return self.abort_with_message(error)

            # Disarm system
            self.security_threads.disarm_system()
            return jsonify({'code': _SUCCESS_CODE,'data': True})

        @app.route('/system/false_alarm', methods=['POST'])
        def set_false_alarm():
            """API route to set security breach as false alarm

            required data:
                rd_mac_address: str
            """
            status, error = self.error_handling.check_system_request(
                request.json, config_key=SecurityClient._FALSE_ALARM_KEY, config_value=self.security_threads.system_breached
            )
            if not status: return self.abort_with_message(error)

            # Set as false alarm
            self.security_threads.false_alarm()
            return jsonify({'code': _SUCCESS_CODE, 'data': True})

        @app.route('/system/location', methods=['POST'])
        def get_gps_location():
            """API route to get gps location coordinates

            required data:
                rd_mac_address: str
            """
            status, error = self.error_handling.check_system_request(request.json)
            if not status: return self.abort_with_message(error)

            data = self.security_threads.hwcontroller.read_gps_sensor()
            if not data:
                error = 'Failed to get GPS data'
                return self.abort_with_message(error)

            _logger.info('Sending gps coordinates to server.')
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

        @app.route('/system/temperature', methods=['POST'])
        def get_temperature():
            """API route to get current temperature data

            required data:
                rd_mac_address: str
            """
            status, error = self.error_handling.check_system_request(request.json)
            if not status: return self.abort_with_message(error)

            data = self.security_threads.hwcontroller.read_temperature_sensor()
            if not data:
                error = 'Failed to get temperature data'
                return self.abort_with_message(error)

            _logger.info('Sending temperature')
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

        @app.route('/system/speedometer', methods=['POST'])
        def get_speedometer_data():
            """API route to get speedometer data

            required data:
                rd_mac_address: str
            """
            status, error = self.error_handling.check_system_request(request.json)
            if not status: return self.abort_with_message(error)

            data = self.security_threads.hwcontroller.read_speedometer_sensor()
            if not data:
                error = 'Failed to get speedometer data'
                return self.abort_with_message(error)

            _logger.info('Sending speedometer data')
            return jsonify({'code': _SUCCESS_CODE, 'data': data})

    def abort_with_message(self, error):
        """error handling method for FLASK API calls

        args:
            message: str

        returns:
            jsonify({code, data, message})
        """
        _logger.info('Aborting with error: [{0}]'.format(message))
        return jsonify({'code': _FAILURE_CODE, 'message': error})

    def start(self):
        """method to start the flask server"""
        app.run(host=self.host, port=self.port)

    def save_settings(self):
        """saves settings before quiting program"""

        self.security_threads.quit_successfully()
