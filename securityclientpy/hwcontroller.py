# -*- coding: utf-8 -*-
#
# hardware controller module
#

import RPi.GPIO as GPIO
import os
import glob
import time
import requests
import gps

from securityclientpy import _logger
from securityclientpy.server_requests import ServerRequests


class HardwareController(object):

    _GPIO_PINS = {'panic_button': 6, 'vibration': 27, 'motion': 22, 'led': 17}
    _THERMAL_SENSOR_BASE_DIR = '/sys/bus/w1/devices/'
    _GEOIP_HOSTNAME = "http://freegeoip.net/json"
    _TEMPERATURE_SIMULATION_DATA = {'fahrenheit': 73.3, 'celcius': 32.0}
    _SPEEDOMETER_SIMLUATION_DATA = {'speed': 75, 'altitude': 1024.6, 'climb': 117}

    def __init__(self, no_hardware, server_host, system_id):
        """set up GPIO and pins as inputs/outputs"""

        self.no_hardware = no_hardware
        self.server_host = server_host
        self.system_id = system_id
        self.server_request = ServerRequests(server_host, system_id)

        if not self.no_hardware:
            self.led_flashing = False

            # Set up sensors and led
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._GPIO_PINS['panic_button'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(self._GPIO_PINS['vibration'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(self._GPIO_PINS['motion'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(self._GPIO_PINS['led'], GPIO.OUT)

            # Panic button callback
            GPIO.add_event_detect(self._GPIO_PINS['panic_button'], GPIO.BOTH, callback=self.panic_button_callback)

            # Set up temperature sensor
            os.system('modprobe w1-gpio')
            os.system('mocprobe w1-therm')
            thermal_sensor_device_folder = glob.glob(self._THERMAL_SENSOR_BASE_DIR + '28*')[0]
            self.thermal_sensor_device_file = thermal_sensor_device_folder + '/w1_slave'

            # Listen on port 2947 (gpsd) of localhost
            self.gps_session = gps.gps("localhost", "2947")
            self.gps_session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

    def status_led_on(self):
        """turn on status led

        before turning on, check if its already on or not
        """
        if not self.no_hardware:
            led_status = GPIO.input(self._GPIO_PINS['led'])
            if not led_status:
                GPIO.output(self._GPIO_PINS['led'], GPIO.HIGH)

    def status_led_off(self):
        """turn off status led

        before turning off, check if its already off or not
        """
        led_status = GPIO.input(self._GPIO_PINS['led'])
        if led_status:
            GPIO.output(self._GPIO_PINS['led'], GPIO.LOW)

    def status_led_flash(self, flashes):
        """flash led a number of times

        before starting the flash, check if its already on or not

        args:
            flashes: int
        """
        if not self.no_hardware:
            led_status = GPIO.input(self._GPIO_PINS['led'])
            if led_status:
                GPIO.output(self._GPIO_PINS['led'], GPIO.LOW)

            for i in range(flashes):
                GPIO.output(self._GPIO_PINS['led'], GPIO.HIGH)
                time.sleep(0.3)
                GPIO.output(self._GPIO_PINS['led'], GPIO.LOW)
                time.sleep(0.3)

    def status_led_flash_start(self):
        """flash status led continuously

        before starting the flash, check if its already on or not

        args:
            flashes: int
        """
        if not self.no_hardware:
            self.led_flashing = True
            led_status = GPIO.input(self._GPIO_PINS['led'])
            if led_status:
                GPIO.output(self._GPIO_PINS['led'], GPIO.LOW)

            while self.led_flashing:
                GPIO.output(self._GPIO_PINS['led'], GPIO.HIGH)
                time.sleep(0.3)
                GPIO.output(self._GPIO_PINS['led'], GPIO.LOW)
                time.sleep(0.3)

    def status_led_flash_stop(self):
        """stops status led flash"""
        if not self.no_hardware:
            self.led_flashing = False
            led_status = GPIO.input(self._GPIO_PINS['led'])
            if led_status:
                GPIO.output(self._GPIO_PINS['led'], GPIO.LOW)

    def _read_thermal_sensor_raw(self):
        """reads raw data from thermal sensor local file

        returns:
            str
        """
        data = None
        try:
            with open(self.thermal_sensor_device_file, 'r') as fp:
                data = fp.readlines()
        except IOError as exception:
            _logger.debug('Could not read file [{0}]'.format(exception))

        return data

    def read_temperature_sensor(self):
        """reads and processes the thermal sensor data from local file

        After data is read from the file, it is converted into celcius and farenheit degrees

        returns:
            float, float
        """
        if self.no_hardware:
            return self._TEMPERATURE_SIMULATION_DATA

        ctemp = 0.0
        ftemp = 0.0
        data = self._read_thermal_sensor_raw()
        if not data:
            return None

        while data[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            data = self._read_thermal_sensor_raw()

        equal_pos = data[1].find('t=')
        if equal_pos != -1:
            data_string = data[1][equal_pos+2:]
            ctemp = float(data_string) / 1000.0
            ftemp = ctemp * 9.0 / 5.0 + 32.0

        return {'fahrenheit': ftemp, 'celcius': ctemp}

    def panic_button_callback(self, channel):
        """callback method for panic push button edge changes

        returns:
            bool
        """
        if self.no_hardware:
            return False
        if GPIO.input(self._GPIO_PINS['panic_button']):
            return self.server_request.send_panic_alert()

    def read_vibration_sensor(self):
        """fetches the current status of the shock sensor via gpio pin

        returns:
            bool
        """
        if self.no_hardware:
            return False
        return GPIO.input(self._GPIO_PINS['vibration'])

    def read_motion_sensor(self):
        """fetches the current status of the motion sensoe via gpio pin

        returns:
            bool
        """
        if self.no_hardware:
            return False
        return GPIO.input(self._GPIO_PINS['motion'])

    def read_speedometer_sensor(self):
        """fetches the current speedometer sensor data via gps module

        returns:
            {speed: int, altitude: float, heading: float, climb: float}
        """
        if self.no_hardware:
            return self._SPEEDOMETER_SIMLUATION_DATA

        data = {}
        try:
            report = self.gps_session.next()
            if report['class'] == 'TPV':
                data = {
                    'speed': report.speed,
                    'altitude': report.alt,
                    'climb': report.climb
                }
        except KeyError:
            pass
        except KeyboardInterrupt:
            pass
        except StopIteration:
            self.gps_session = None

        return data

    def read_gps_sensor(self):
        """fetches the current gps sensor data via gps module

        returns:
            {latitude, longitude}
        """
        if self.no_hardware:
            geo = requests.get(self._GEOIP_HOSTNAME)
            json_data = geo.json()
            data = {
                "latitude": float(json_data["latitude"]),
                "longitude": float(json_data["longitude"])
            }
            return data

        data = {}
        try:
            report = self.gps_session.next()
            if report['class'] == 'TPV':
                data = {
                    'latitude': report.lat,
                    'longitude': report.lon
                }
        except KeyError:
            pass
        except KeyboardInterrupt:
            pass
        except StopIteration:
            self.gps_session = None

        return data

    def cleanup(self):
        if not self.no_hardware:
            GPIO.cleanup()
            self.gps_session = None