# -*- coding: utf-8 -*-
#
# hardware controller used to control gpio and cameras
#

# import RPi.GPIO as GPIO
import os
import glob
import time
# import gps

from securityclientpy import _logger


class HardwareController(object):
    """controller class for hardware components"""

    _PANIC_BUTTON = 32
    _SHOCK_SENSOR = 27
    _NOISE_SENSOR = 12
    _MOTION_SENSOR = 22
    _STATUS_LED = 17
    _THERMAL_SENSOR = 4
    _THERMAL_SENSOR_BASE_DIR = '/sys/bus/w1/devices/'

    def __init__(self):
        """set up GPIO and pins as inputs/outputs"""

        self.led_flashing = False

        # Set up panic button
        GPIO.setup(HardwareController._PANIC_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Set up shock sensor
        GPIO.setup(HardwareController._SHOCK_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Set up thermal sensor
        os.system('modprobe w1-gpio')
        os.system('mocprobe w1-therm')
        thermal_sensor_device_folder = glob.glob(HardwareController._THERMAL_SENSOR_BASE_DIR + '28*')[0]
        self.thermal_sensor_device_file = thermal_sensor_device_folder + '/w1_slave'

        # Set up noise sensor
        GPIO.setup(HardwareController._NOISE_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # Set up status led
        GPIO.setup(HardwareController._STATUS_LED, GPIO.OUT)

        # Listen on port 2947 (gpsd) of localhost
        self.gps_session = gps.gps("localhost", "2947")
        self.gps_session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

    def status_led_on(self):
        """turn on status led

        before turning on, check if its already on or not
        """
        led_status = GPIO.input(HardwareController._STATUS_LED)
        if not led_status:
            GPIO.output(HardwareController._STATUS_LED, GPIO.HIGH)

    def status_led_off(self):
        """turn off status led

        before turning off, check if its already off or not
        """
        led_status = GPIO.input(HardwareController._STATUS_LED)
        if led_status:
            GPIO.output(HardwareController._STATUS_LED, GPIO.LOW)

    def status_led_flash(self, flashes):
        """flash led a number of times

        before starting the flash, check if its already on or not

        args:
            flashes: int
        """
        led_status = GPIO.input(HardwareController._STATUS_LED)
        if led_status:
            GPIO.output(HardwareController._STATUS_LED, GPIO.LOW)

        for i in range(flashes):
            GPIO.output(HardwareController._STATUS_LED, GPIO.HIGH)
            time.sleep(0.3)
            GPIO.output(HardwareController._STATUS_LED, GPIO.LOW)
            time.sleep(0.3)

    def status_led_flash_start(self):
        """flash status led continuously

        before starting the flash, check if its already on or not

        args:
            flashes: int
        """
        self.led_flashing = True
        led_status = GPIO.input(HardwareController._STATUS_LED)
        if led_status:
            GPIO.output(HardwareController._STATUS_LED, GPIO.LOW)

        while self.led_flashing:
            GPIO.output(HardwareController._STATUS_LED, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(HardwareController._STATUS_LED, GPIO.LOW)
            time.sleep(0.5)

    def status_led_flash_stop(self):
        """stops status led flash"""
        self.led_flashing = False
        led_status = GPIO.input(HardwareController._STATUS_LED)
        if led_status:
            GPIO.output(HardwareController._STATUS_LED, GPIO.LOW)

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

    def read_thermal_sensor(self):
        """reads and processes the thermal sensor data from local file

        After data is read from the file, it is converted into celcius and farenheit degrees

        returns:
            float, float
        """
        ctemp = None
        ftemp = None
        data = self._read_thermal_sensor_raw()

        while data[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            data = self._read_thermal_sensor_raw()

        equal_pos = data[1].find('t=')
        if equal_pos != -1:
            data_string = lines[1][equal_pos+2:]
            ctemp = float(data_string) / 1000.0
            ftemp = ctemp * 9.0 / 5.0 + 32.0

        return {'fahrenheit': ftemp, 'celcius': ctemp}

    def read_noise_sensor(self):
        """fetches the current dbs of the noise sensor

        returns:
            int (maybe float), to be determined
        """
        pass

    def read_panic_button(self):
        """fetches the current status of the panic button via gpio pin

        returns:
            bool
        """
        return GPIO.input(HardwareController._PANIC_BUTTON)

    def read_shock_sensor(self):
        """fetches the current status of the shock sensor via gpio pin

        returns:
            bool
        """
        return GPIO.input(HardwareController._SHOCK_SENSOR)

    def read_motion_sensor(self):
        """fetches the current status of the motion sensoe via gpio pin

        returns:
            bool
        """
        return GPIO.input(HardwareController._MOTION_SENSOR)

    def read_speedometer_sensor(self):
        """fetches the current speedometer sensor data via gps module

        returns:
            {speed: int, altitude: float, heading: float, climb: float}
        """
        data = {}
        try:
            report = self.gps_session.next()
            if report['class'] == 'TPV':
                data = {
                    'speed': report.speed,
                    'altitude': report.altitude,
                    'heading': report.heading,
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
        data = {}
        try:
            report = self.gps_session.next()
            if report['class'] == 'TPV':
                data = {
                    'latitude': report.latitude,
                    'longitude': report.longitude
                }
        except KeyError:
            pass
        except KeyboardInterrupt:
            pass
        except StopIteration:
            self.gps_session = None

        return data