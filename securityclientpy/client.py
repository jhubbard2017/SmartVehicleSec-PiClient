# -*- coding: utf-8 -*-
#
# client module
#

from securityclientpy import _logger, get_mac_address, port
from securityclientpy.server_requests import ServerRequests
from securityclientpy.routes.security import Security
from securityclientpy.routes.system import System
from securityclientpy.hwcontroller import HardwareController
from securityclientpy.routes import app


class Client(object):
    """security client class"""

    def __init__(self, host, serverhost, no_hardware=False, no_video=False, dev=False, testing=False):
        """constructor method"""
        self.host = host
        self.system_id = self.get_device_id(dev, testing)
        _logger.info('System ID = {0}'.format(self.system_id))
        self.server_requests = ServerRequests(serverhost, self.system_id)
        self.hwcontroller = HardwareController(no_hardware, self.server_requests)

        # Routes
        self.security = Security(no_hardware, no_video, self.system_id, self.hwcontroller, self.server_requests)
        self.system = System(self.system_id, self.hwcontroller)

        # Initialize system with server
        self._initialize_client()

    def _initialize_client(self):
        """method to update security client on server and locally"""

        connection_exist = self.server_requests.get_connection()
        if connection_exist == None: return

        if connection_exist:
            if not self.server_requests.update_connection(self.host, port): return
            config = self.server_requests.get_security_config()
            if not config: return

            # Update local security configs
            self.security.security_threads.system_armed = config['system_armed']
            self.security.security_threads.system_breached = config['system_breached']
        else:
            if not self.server_requests.add_connection(self.host, port): return
            if not self.server_requests.add_security_config(): return

        _logger.info('Successfully initialized system')

    def start(self):
        """method to start the flask server"""
        app.run(host=self.host, port=port)

    def save_settings(self):
        """method is fired when the user disconnects or the socket connection is broken"""

        _logger.info('Saving security session.')
        self.security.security_threads.quit_successfully()

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
        elif dev:
            return 'DEVELOP'
        else:
            return get_mac_address()
