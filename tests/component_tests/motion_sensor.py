# -*- coding: utf-8 -*-
#
# module for testing the motion sensor
#

import RPi.GPIO as GPIO
import time
from threading import Thread

class motionDetectionTest(object):

    MOTION_SENSOR = 22

    def __init__(self):
        # Constructor method
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.MOTION_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.thread_running = True

    def read_motion_sensor(self):
        """fetches the current status of the motion sensoe via gpio pin

        returns:
            bool
        """
        return GPIO.input(self.MOTION_SENSOR)

    def check_motion(self):
        while self.thread_running:
            motion_detected = self.read_motion_sensor()
            if motion_detected:
                print("Motion detected")
            else:
                print("No motion detected")
            time.sleep(0.5)

def main():
    print("Checking motion...")
    sensor_test = motionDetectionTest()
    thread = Thread(target=sensor_test.check_motion)
    thread.start()
    time.sleep(10)
    sensor_test.thread_running = False
    print("Program terminated...")

if __name__ == '__main__':
    main()
