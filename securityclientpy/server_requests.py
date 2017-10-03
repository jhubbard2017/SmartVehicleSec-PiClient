# -*- coding: utf-8 -*-
#
# module for handling api request made to server
#

import requests

from securityclientpy import _logger


class ServerRequests(object):
    """module for handling api request made to server"""

    _SUCCESS_CODE = 201
    _FAILURE_CODE = 404

    def __init__(self, serverhost, serverport, device_id):
        """constructor method"""
        self.url = 'http://{0}:{1}/system'.format(serverhost, serverport)
        self.data = {'rd_mac_address': device_id}

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
        path = 'update_connection'
        data = {'ip_address': self.host, 'port': self.port}
        response = self.request(path, data)
        if response['code'] == self._FAILURE_CODE:
            _logger.info('Failed to update connection: [{0}]'.format(response['message']))
            return False

        return True

    def add_connection(self):
        """method to send server request for adding connection on the server

        returns:
            bool
        """
        path = 'add_connection'
        data = {'ip_address': self.host, 'port': self.port}
        response = self.request(path, data)
        if not response['code'] == self._FAILURE_CODE:
            _logger.info('Failed to add connection: [{0}]'.format(response['message']))
            return False

        return True

    def get_connection(self):
        """method to send server request for checking if connection exist on server

        returns:
            bool
        """
        path = 'get_connection'
        response = self.request(path)
        if response['code'] == self._FAILURE_CODE:
            _logger.info('Failed to get connection: [{0}]'.format(response['message']))
            return None

        status = response['data']
        return status

    def get_security_config(self):
        """method to send server request for updating local security config with that which is on the server

        returns:
            dict(system_armed, system_breached)
        """
        path = 'security_config'
        response = self.request(path)
        if not response['code'] == self._FAILURE_CODE:
            _logger.info('Failed to get security config: [{0}]'.format(response['message']))
            return None

        config = response['data']
        return config

    def create_security_config(self):
        """method to send server request for creating a new security config

        returns:
            bool
        """
        path = 'create_securityconfig'
        response = self.request(path)
        if response['code'] == self._FAILURE_CODE:
            _logger.info('Failed to create security config: [{0}]'.format(response['message']))
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
        if  response['code'] == self._FAILURE_CODE:
            _logger.info('Failed to send speed limit alert: [{0}]'.format(response['message']))
            return False

        return True