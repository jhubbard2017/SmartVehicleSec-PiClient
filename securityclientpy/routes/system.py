# -*- coding: utf-8 -*-
#
# systems module
#

from flask import request

from securityclientpy.routes import app, verify_request, error_response, success_response
from securityclientpy.hwcontroller import HardwareController


class System(object):

    _ROOT_PATH = '/system'

    def __init__(self, no_hardware, server_host, system_id):
        self.system_id = system_id
        self.hwcontroller = HardwareController(no_hardware, server_host, system_id)

        # Use inner methods so self pointer can be accessed

        @app.route('{0}/location'.format(self._ROOT_PATH), methods=['POST'])
        def location():
            """get location data

            required data:
                system_id: str
            """
            status, error = verify_request(request.json, self.system_id)
            if not status: return error_response(error)

            data = self.hwcontroller.read_gps_sensor()
            if not data: return error_response('Unable to get location data')

            return success_response(request.path, data=data)

        @app.route('{0}/temperature'.format(self._ROOT_PATH), methods=['POST'])
        def temperature():
            """get temperature data

            required data:
                system_id: str
            """
            status, error = verify_request(request.json, self.system_id)
            if not status: return error_response(error)

            data = self.hwcontroller.read_temperature_sensor()
            if not data: return error_response('Unable to get temperature data')

            return success_response(request.path, data=data)

        @app.route('{0}/speedometer'.format(self._ROOT_PATH), methods=['POST'])
        def speedometer():
            """get speedometer data

            required data:
                system_id: str
            """
            status, error = verify_request(request.json, self.system_id)
            if not status: return error_response(error)

            data = self.hwcontroller.read_speedometer_sensor()
            if not data: return error_response('Unable to get speedometer data')

            return success_response(request.path, data=data)
