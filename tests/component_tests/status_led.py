# -*- coding: utf-8 -*-
#
# module for testing the status led
#

import RPi.GPIO as GPIO
import time


class statusLEDTest(object):

    STATUS_LED = 17

    def __init__(self):
        # Constructor method
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.STATUS_LED, GPIO.OUT)

    def set_led_output(self, status):
        """turns LED on and off

        args:
            status: bool

        returns:
            bool
        """
        if status:
            GPIO.output(self.STATUS_LED, GPIO.HIGH)
        else:
            GPIO.output(self.STATUS_LED, GPIO.LOW)

    def get_led_status(self):
        return GPIO.input(self.STATUS_LED)


def main():
    test = statusLEDTest()
    for i in range(10):
        status = test.get_led_status()
        if status:
            test.set_led_output(False)
        else:
            test.set_led_output(True)
        time.sleep(1)

if __name__ == '__main__':
    main()
