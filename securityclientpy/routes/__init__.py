# -*- coding: utf-8 -*-
#
# useful objects and methods for api calls
#

from flask import Flask, jsonify
from securityclientpy import _logger
from securityclientpy.hwcontroller import HardwareController

app = Flask(__name__)

# Constants
_SUCCESS_CODE = 201
_FAILURE_CODE = 404

# Error message keys
_DEVICE_KEY = 'system_id'
_ARM_SYSTEM_KEY = 'arm_system'
_DISARM_SYSTEM_KEY = 'disarm_system'
_FALSE_ALARM_KEY = 'false_alarm'

_CONFIG_ERROR_VALUES = {
    'arm_system': {'value': True, 'message': 'System already armed'},
    'disarm_system': {'value': False, 'message': 'System already disarmed'},
    'false_alarm': {'value': False, 'message': 'System is not breached'}
}

def verify_request(json, config_key=None, config_value=None):
    """checks the request to arm the system for errors

    returns:
        bool, str
    """
    if not json:
        error_message = 'No data found in request'
        return (False, error_message)

    if not 'system_id' in json:
        error_message = 'No device found in request'
        return (False, error_message)

    system_id = json['system_id']
    if system_id != self.system_id:
        error = 'Invalid system ID'
        return (False, error)

    if config_key:
        current_config = _CONFIG_ERROR_VALUES[config_key]
        if current_config['value'] == config_value:
            return (False, current_config['message'])

    return (True, None)

def error_response(error):
    """error handling method for FLASK API calls

    args:
        message: str

    returns:
        jsonify({code, data, message})
    """
    _logger.info('Aborting with error: [{0}]'.format(error))
    return jsonify({'code': _FAILURE_CODE, 'message': error})

def success_response(path, data=True):
    """success handling method for FLASK API calls

    args:
        path: str
        data: Any (Default=True)
    """
    _logger.info('Success for path [{0}] data [{1}]'.format(path, data))
    return jsonify({'code': _SUCCESS_CODE, 'data': data})
