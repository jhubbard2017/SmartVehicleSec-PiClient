# -*- coding: utf-8 -*-
#
# main file: smart vehicle security server
#

import os
from argparse import ArgumentParser
from threading import Thread
import sys

from securityclientpy import _logger
from securityclientpy.version import __version__
from securityclientpy.securityclient import SecurityClient


def _config_from_args():
    """sets up argparse to parse command line args

    returns:
        argparse.ArgumentParser
    """
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    optional_argument_group = parser.add_argument_group('optional arguments')
    optional_argument_group.add_argument(
        '-i', '--host', dest='host', default=None, required=True,
        help='Port number used for clients to access server. ')
    optional_argument_group.add_argument(
        '-p', '--port', dest='port', default=None, required=True,
        help='Port number used for clients to access server. ')
    optional_argument_group.add_argument(
        '-nh', '--no_hardware', dest='no_hardware', action='store_true', default=False, required=False,
        help='Will not attempt to use any hardware.')
    optional_argument_group.add_argument(
        '-nv', '--no_video', dest='no_video', action='store_true', default=False, required=False,
        help='Will not attempt to use any hardware.')
    optional_argument_group.add_argument(
        '-dev', '--develop', dest='dev', action='store_true', default=False, required=False,
        help='Will not attempt to use any hardware.')

    return parser.parse_args()

# Make global so can be accessed when need to stop system, and safely save settings
config = _config_from_args()
port = int(config.port)
sec_server = SecurityClient(host=config.host, port=port,
                            no_hardware=config.no_hardware, no_video=config.no_video, dev=config.dev)

def main_thread():
    """main thread to start up the server"""
    sec_server.start()

def main():
    """ main function

    set up configs and start server
        - Enter 'stop' to end the server and successfully save settings
    """
    thread = Thread(target=main_thread)
    thread.daemon = True
    thread.start()
    while True:
        text = raw_input()
        if text == "stop":
            _logger.info("Shutting down. Saving settings.")
            sec_server.save_settings()
            sys.exit(0)

if __name__ == '__main__':
    main()
