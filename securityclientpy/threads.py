# -*- coding: utf-8 -*-
#
# module for controlling all security threads
#

from threading import Thread
import time

from securityclientpy import _logger
from securityclientpy.hwcontroller import HardwareController
from securityclientpy.videostreamer import VideoStreamer
from securityclientpy.server_requests import ServerRequests


class SecurityThreads(object):
    """module for controlling all security threads"""

    # Constants
    _DEFAULT_CAMERA_ID = 0
    _MAX_TEMP = 85.0
    _FLASH_SYSTEM_ARMED = 6
    _FLASH_SYSTEM_DISARMED = 3
    _FLASH_FALSE_ALARM = 2

    def __init__(self, serverhost, serverport, no_hardware, no_video, device_id):
        """constructor method"""
        self._system_armed = False
        self._system_breached = False
        self.no_hardware = no_hardware
        self.no_video = no_video
        self.initial_motion_detected = False
        self.speed_checker_thread_running = False

        self.server_requests = ServerRequests(serverhost, serverport, device_id)

        # Create objects for different config/development levels
        self.hwcontroller = HardwareController(no_hardware)
        if not self.no_video:
            self.videostream = VideoStreamer(SecurityThreads._DEFAULT_CAMERA_ID)

    def arm_system(self):
        """method to arm system"""

        if self._system_armed: return
        self._system_armed = True
        self.hwcontroller.status_led_flash(SecurityThreads._FLASH_SYSTEM_ARMED)

        # Start system armed thread
        thread = Thread(target=self._armed)
        thread.start()

    def disarm_system(self):
        """method to disarm system"""

        if not self._system_armed: return
        self._system_armed = False
        self.hwcontroller.status_led_flash(SecurityThreads._FLASH_SYSTEM_DISARMED)

    def false_alarm(self):
        """method to set breach as false alarm"""

        if not self._system_breached: return
        self._system_breached = False
        self.hwcontroller.status_led_flash(SecurityThreads._FLASH_FALSE_ALARM)

    def _armed(self):
        """method to run when the system is armed"""
        _logger.info('System will arm in 5 secs')
        time.sleep(5)
        _logger.info('System armed')

        # Initialize variables in case they aren't used (so checking doesn't throw error)
        temp = None
        motion = None
        noise = None

        self.initial_motion_detected = self.initial_motion_detected()
        while self._system_armed:
            if not self.no_hardware:
                if self.initial_motion_detected:
                    temp = self.hwcontroller.read_thermal_sensor()
                    temp = temp['fahrenheit']
                else:
                    motion = self.hwcontroller.read_motion_sensor()
                    noise = self.hwcontroller.read_noise_sensor()
                shock = self.hwcontroller.read_shock_sensor()

                if motion or noise or shock:
                    # Start breached thread
                    self._system_breached = True
                    thread = Thread(target=self._breached)
                    thread.start()
                    break

                if temp and temp >= SecurityThreads._MAX_TEMP:
                    # Notify server of dangerous temp
                    pass

        _logger.info('System disarmed')

    def _breached(self):
        """method to run when system is breached"""
        _logger.info('System breached.')

        # Set up video file and start streaming
        fourcc = cv2.cv.CV_FOURCC(*'XVID')  # cv2.VideoWriter_fourcc() does not exist
        video_writer = cv2.VideoWriter("system-breach-recording-{:%b %d, %Y %-I:%M %p}.avi".format(datetime.datetime().now()),
                                       fourcc, 20, (680, 480))
        while self.system_breached:
            if not self.no_video:
                status, frame_jpeg, frame = self.videostream.read()
                if status:
                    video_writer.write(frame)

        _logger.info('System breach ended')

    def initial_motion_is_detected(self):
        """checks if motion is detected for a time of 3 seconds before arming system

        returns:
            bool
        """
        motion_detected = False
        if not self.no_hardware:
            for x in range(3):
                motion_detected = self.hwcontroller.read_motion_sensor()
                if motion_detected: break
                time.sleep(1)

        return motion_detected

    def start_speed_checking_thread(self):
        """method to start checking for speeding"""

        thread = Thread(target=self.main_speed_checking_thread)
        thread.start()
        self.speed_checker_thread_running = True

    def main_speed_checking_thread(self):
        """main thread for keeping up with the speed and speed limit

        This thread will run and update the speeding status every 30 seconds
        """
        _logger.debug('Speed checking thread started.')
        while self.speed_checker_thread_running:
            # Check data
            coordinates = self.get_gps_coordinates()
            speed_limits = self.get_speed_limits(coordinates)
            speed = self.get_current_speed()
            for speed_limit in speed_limits:
                if self.is_over_speed_limit(speed, speed_limit):
                    self.server_requests.send_speed_limit_alert()
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

    # ------------------------------------ GETTERS AND SETTERS  ------------------------------------ #

    @property
    def system_armed(self):
        return self._system_armed

    @system_armed.setter
    def system_armed(self, value):
        self._system_armed = value

    @property
    def system_breached(self):
        return self._system_breached

    @system_breached.setter
    def system_breached(self, value):
        self._system_breached = value

        # ------------------------------------ QUITTING METHODS  ------------------------------------ #

    def quit_successfully(self):
        """method to peacfully close all threads and videostreeams"""
        if not self.no_video:
            self.videostream.release_stream()
        if not self.no_hardware:
            self.speed_checker_thread_running = False