# -*- coding: utf-8 -*-
#
# methods for providing a device id depending on development level
#

import netifaces

def get_mac_address():
    """method to get the MAC address of the raspberry pi using eth0 interface

    returns:
        str
    """
    eth0_interface = 'eth0'
    addresses = netifaces.ifaddresses(eth0_interface)[netifaces.AF_LINK][0]
    mac_address = addresses['addr']
    return mac_address