# -*- coding: utf-8 -*-
#
# server requests module
#

import requests

from securityclientpy import _logger, host, port, serverport
from securityclientpy.routes import _FAILURE_CODE


class ServerRequests(object):
    """module for handling api request made to server"""

    def __init__(self, serverhost, system_id):
        """constructor method"""
        self.url = 'http://{0}:{1}'.format(serverhost, serverport)
        self.data = {'system_id': system_id}

    def request(self, path, data={}):
        """method to send request to server and get the response

        args:
            url: str
            data: dict

        returns:
            dict
        """
        url = '{0}/{1}'.format(self.url, path)
        request_data = self.data
        for key, value in data.iteritems():
            request_data[key] = value
        response = requests.post(url, json=request_data)
        if not response.json():
            return None

        return response.json()

    def update_connection(self):
        """method to send server request for updating connection on the server

        returns:
            bool
        """
        path = 'connections/update'
        data = {'host': host, 'port': port}
        response = self.request(path, data)
        if response['code'] == _FAILURE_CODE:
            _logger.info('Failed to update connection: [{0}]'.format(response['message']))
            return False

        return True

    def add_connection(self):
        """method to send server request for adding connection on the server

        returns:
            bool
        """
        path = 'connections/add'
        data = {'host': host, 'port': port}
        response = self.request(path, data)
        if response['code'] == _FAILURE_CODE:
            _logger.info('Failed to add connection: [{0}]'.format(response['message']))
            return False

        return True

    def get_connection(self):
        """method to send server request for checking if connection exist on server

        returns:
            bool
        """
        path = 'connections/get'
        response = self.request(path)
        if response['code'] == _FAILURE_CODE:
            _logger.info('Failed to get connection: [{0}]'.format(response['message']))
            return None

        return response['data']

    def get_security_config(self):
        """method to send server request for updating local security config with that which is on the server

        returns:
            dict(system_armed, system_breached)
        """
        path = 'security/get_config'
        response = self.request(path)
        if response['code'] == _FAILURE_CODE:
            _logger.info('Failed to get security config: [{0}]'.format(response['message']))
            return None

        return response['data']

    def add_security_config(self):
        """method to send server request for creating a new security config

        returns:
            bool
        """
        path = 'security/add_config'
        response = self.request(path)
        if response['code'] == _FAILURE_CODE:
            _logger.info('Failed to add security config: [{0}]'.format(response['message']))
            return False

        return True

    def send_speed_limit_alert(self):
        """sends post request to server to alert for driving over the speed limit

        returns:
            bool
        """
        path = 'notification'
        message = 'You are exceeding the speed limit'
        data = {'message': message}
        response = self.request(path, data)
        if response['code'] == _FAILURE_CODE:
            _logger.info('Failed to send speed limit alert: [{0}]'.format(response['message']))
            return False

        return True
