# -*- coding: utf-8 -*-
#
# module for testing the temperature sensor
#

import time
from threading import Thread
import os
import glob

class temperatureDetectionTest(object):

    _THERMAL_SENSOR_BASE_DIR = '/sys/bus/w1/devices/'

    def __init__(self):
        thermal_sensor_device_folder = glob.glob(self._THERMAL_SENSOR_BASE_DIR + '28*')[0]
        self.thermal_sensor_device_file = thermal_sensor_device_folder + '/w1_slave'
        self.thread_running = True

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

        return ftemp, ctemp

    def check_temperature(self):
        while self.thread_running:
            ftemp, ctemp = self.read_temperature_sensor()
            print("Temperature: {0} F, {1} C".format(ftemp, ctemp))
            time.sleep(0.5)


def main():
    print("Checking temperature...")
    sensor_test = temperatureDetectionTest()
    thread = Thread(target=sensor_test.check_temperature)
    thread.start()
    time.sleep(15)
    sensor_test.thread_running = False
    print("Program terminated...")

if __name__ == '__main__':
    main()