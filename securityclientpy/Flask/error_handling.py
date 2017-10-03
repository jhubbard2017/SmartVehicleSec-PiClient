# -*- coding: utf-8 -*-
#
# module for handling errors made during rest api calls from clients
#

from securityclientpy import _logger


class APIErrorHandling(object):

    _DEVICE_KEY = 'rd_mac_address'
    _CONFIG_ERROR_VALUES = {
        'arm_system': {'value': True, 'message': 'System already armed'},
        'disarm_system': {'value': False, 'message': 'System already disarmed'},
        'false_alarm': {'value': False, 'message': 'System is not breached'}
    }

    def __init__(self, device_id):
        self.device_id = device_id

    def _check_json(self, json):
        """checks if keys are located in a json object

        args:
            json: {}
            keys: [str]

        returns:
            bool, str
        """
        if not json:
            error_message = 'No data found in request'
            return (False, error_message)

        if not APIErrorHandling._DEVICE_KEY in json:
            error_message = 'No device found in request'
            return (False, error_message)

        return (True, None)


    def check_system_request(self, json, config_key=None, config_value=None):
        """checks the request to arm the system for errors

        returns:
            bool, str
        """
        status, error = self._check_json(json)
        if not status:
            return (False, error)

        device_id = json[APIErrorHandling._DEVICE_KEY]
        if device_id != self.device_id:
            error = 'Invalid device ID'
            return (False, error)

        if config_key:
            current_config = APIErrorHandling._CONFIG_ERROR_VALUES[config_key]
            if current_config['value'] == config_value:
                return (False, current_config['message'])

        return (True, None)
