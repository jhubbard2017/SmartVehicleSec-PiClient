# -*- coding: utf-8 -*-
#
# security module
#

from flask import request

from securityclientpy import _logger
from securityclientpy.routes import app, verify_request, error_response, success_response
from securityclientpy.threads import SecurityThreads


class Security(object):

    _ROOT_PATH = '/security'
    _ARM_SYSTEM_KEY = 'arm_system'
    _DISARM_SYSTEM_KEY = 'disarm_system'
    _FALSE_ALARM_KEY = 'false_alarm'

    def __init__(self, no_hardware, no_video, serverhost, system_id):
        self.system_id = system_id
        self.security_threads = SecurityThreads(no_hardware, no_video, serverhost, self.system_id)

        # Use inner methods so self pointer can be accessed

        @app.route('{0}/arm'.format(self._ROOT_PATH), methods=['POST'])
        def arm():
            """arm system

            required data:
                system_id: str
            """
            status, error = verify_request(
                request.json, self.system_id, config_key=self._ARM_SYSTEM_KEY, config_value=False
            )
            if not status: return error_response(error)

            self.security_threads.arm_system()
            return success_response(request.path)

        @app.route('{0}/disarm'.format(self._ROOT_PATH), methods=['POST'])
        def disarm():
            """disarm system

            required data:
                system_id: str
            """
            status, error = verify_request(
                request.json, self.system_id, config_key=self._DISARM_SYSTEM_KEY, config_value=True
            )
            if not status: return error_response(error)

            self.security_threads.disarm_system()
            return success_response(request.path)

        @app.route('{0}/false_alarm'.format(self._ROOT_PATH), methods=['POST'])
        def false_alarm():
            """set system breach as false alarm

            required data:
                system_id: str
            """
            status, error = verify_request(
                request.json, self.system_id, config_key=self._FALSE_ALARM_KEY, config_value=True
            )
            if not status: return error_response(error)

            self.security_threads.false_alarm()
            return success_response(request.path)
