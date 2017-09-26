# -*- coding: utf-8 -*-
#
# error handling for flask
#

from securityclientpy import _logger

class FlaskErrorHandling(object):

    _DEVICE_KEY = 'rd_mac_address'
    _CONFIG_PREV_VALUES = {
        'arm_system': {'unexpected_value': True, 'error_message': 'System already armed'},
        'disarm_system': {'unexpected_value': False, 'error_message': 'System already disarmed'},
        'false_alarm': {'unexpected_value': False, 'error_message': 'System is not breached'}
    }

    def __init__(self, device_id):
        self.device_id = device_id

    def _check_json_for_error(self, json):
        """checks if keys are located in a json object

        args:
            json: {}
            keys: [str]

        returns:
            bool, str
        """
        error_found = True
        if not json:
            error_message = 'No data found in request'
            return error_found, error_message

        if not FlaskErrorHandling._DEVICE_KEY in json:
            error_message = 'No device found in request'
            return error_found, error_message

        return not error_found, None


    def check_system_request(self, json, config_key=None, config_value=None):
        """checks the request to arm the system for errors

        returns:
            status, error
        """
        error_found = True
        error_found, error = self._check_json_for_error(json)
        if error_found:
            return error_found, error

        expected_device_id = json[FlaskErrorHandling._DEVICE_KEY]
        if expected_device_id != self.device_id:
            error = 'Invalid device ID'
            return error_found, error

        if config_key:
            current_config = FlaskErrorHandling._CONFIG_PREV_VALUES[config_key]
            if current_config['unexpected_value'] == config_value:
                return error_found, current_config['error_message']

        return not error_found, None
