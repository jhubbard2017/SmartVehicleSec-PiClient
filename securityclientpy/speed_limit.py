# -*- coding: utf-8 -*-
#
# Logic for getting the speed limit for a particular set of gps coordinates and comparing to vehicle speed limit
#

import RPi.GPIO as GPIO
import overpy
import sys
import time
from threading import Thread

from securityclientpy import _logger
from securityclientpy.hwcontroller import HardwareController

class SpeedLimit(object):
    """Module to Get current speed limit within a certain radius of GPS coordinates
        and determine whether the user is driving over the speed limit of not.

        When this action occurs, we want to send a notification to the user, and to the parents of the user (if under 18)
        to slow down while driving.
    """

    _RADIUS = 100
    _SLEEP_SECONDS = 30

    def __init__(self, host, port, mac_address):
        self.host = host
        self.port = port
        self.mac_address = mac_address
        self.hwcontroller = HardwareController()

        thread = Thread(target=self.main_speed_checking_thread)
        thread.start()
        self.thread_running = True

    def main_speed_checking_thread(self):
        """main thread for keeping up with the speed and speed limit

        This thread will run and update the speeding status every 30 seconds
        """
        _logger.debug('Speed checking thread started.')
        while self.thread_running:
            # Check data
            coordinates = self.get_gps_coordinates()
            speed_limits = self.get_speed_limits(coordinates)
            speed = self.get_current_speed()
            for speed_limit in speed_limits:
                if self.is_over_speed_limit(speed, speed_limit):
                    self.alert_server()
            time.sleep(SpeedLimit._SLEEP_SECONDS)

        _logger.debug('Speed checking thread stopped.')


    def get_speed_limits(self, coordinates):
        """Get the speed limit within a certain radius of particular gps coordinates

        returns:
            [{name, speed_limit}]
        """
        latitude = coordinates['latitude']
        longitude = coordinates['longitude']
        api = overpy.Overpass()

        # fetch all ways and nodes
        result = api.query("""
            way(around:""" + str(SpeedLimit._RADIUS) + """,""" + str(latitude) + """,""" + str(longitude)  + """) ["maxspeed"];
                (._;>;);
                    out body;
                        """)
        results_list = []
        for way in result.ways:
            road = {}
            road["name"] = way.tags.get("name", "n/a")
            road["speed_limit"] = way.tags.get("maxspeed", "n/a")
            nodes = []
            for node in way.nodes:
                nodes.append((node.lat, node.lon))
            road["nodes"] = nodes
            results_list.append(road)
        return results_list

    def get_current_speed(self):
        """Gets the current speed from the GPS sensor in the hardware controller

        returns:
            float
        """
        speedometer_data = self.hwcontroller.read_speedometer_sensor()
        current_speed = speedometer_data['speed']
        return current_speed

    def get_gps_coordinates(self):
        """Gets the gps current gps coordinates from the gps sensor in the hardware controller

        returns:
            {latitude, longitude}
        """
        gps_data = self.hwcontroller.read_gps_sensor()
        return gps_data

    def is_over_speed_limit(self, speed, speed_limit):
        """compares the speed with a speed limit in a certain area

        Since the grace amount of speeding is technically around 10 mph over the speed limit,
        We increment the speed limit by 10 and then make the comparison

        args:
            speed: float
            speed_limit: float

        returns:
            bool
        """
        return speed > speed_limit + 10.0

    def alert_server(self):
        """sends post request to server to alert for driving over the speed limit

        returns:
            bool
        """
        url = 'http://{0}:{1}/system/notification'.format(self.host, self.port)
        message = 'You are exceeding the speed limit'
        data = {'rd_mac_address': self.mac_address, 'message': message}
        response = requests.post(url, json=data)
        json_data = response.json()
        if not json_data['data']:
            _logger.info('Failed to add connection on server')
            return False

        return True

    def stop_thread(self):
        self.thread_running = False