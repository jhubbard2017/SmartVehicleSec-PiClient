# -*- coding: utf-8 -*-
#
# logic for establing server communication, processing data, and sending data to clients
#

from securityclientpy import _logger
from securityclientpy.Flask.restapi import RestAPI
from securityclientpy.get_device_id import get_mac_address
from securityclientpy.server_requests import ServerRequests


class SecurityClient(object):
    """security client class"""

    def __init__(self, host, port, serverhost, serverport, no_hardware=False, no_video=False, dev=False, testing=False):
        """constructor method"""

        self.host = host
        self.port = port
        self.serverhost = serverhost
        self.serverport = serverport

        device_id = self.get_device_id(dev, testing)
        self.restapi = RestAPI(host, port, serverhost, serverport, no_hardware, no_video, device_id)
        self.server_requests = ServerRequests(serverhost, serverport, device_id)
        self._initialize_client()

    def _initialize_client(self):
        """method to update security client on server and locally"""

        connection_exist = self.server_requests.get_connection()
        if connection_exist == None: return

        if connection_exist:
            if not self.server_requests.update_connection(): return
            config = self.server_requests.get_security_config()
            if not config: return

            # Update local security configs
            self.restapi.security_threads.system_armed = config['system_armed']
            self.restapi.security_threads.system_breached = config['system_breached']
        else:
            if not self.server_requests.add_connection(): return
            if not self.server_requests.create_security_config(): return

        _logger.info('Successfully initialized system')

    def start(self):
        """method to start the server"""
        self.restapi.start()

    def save_settings(self):
        """method is fired when the user disconnects or the socket connection is broken"""

        _logger.info('Saving security session.')
        self.restapi.save_settings()

    def get_device_id(self, dev, testing):
        """method to get particular device id for different development levels

        args:
            dev: bool
            testing: bool

        returns:
            str
        """
        if testing:
            return 'TESTING'
        if dev:
            return 'DEVELOP'
        else:
            return get_mac_address()
