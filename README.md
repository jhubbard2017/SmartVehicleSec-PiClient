# Smart Vehicle Security Server
Python client software for the Smart Vehicle Security System (Raspberry Pi Client).

## Usage Examples
### running on local machine and raspberry pi
- this example assumes a python virtual env has already been established - see details on virtual env
- this example does not trigger any calls to hardware devices or video devices
```shell
(venv-securityclientpy) $ securityclientpy -si host 
```
- the required arguments are the ip address and port number. These two need to be specified to start the program.
- Optional arguments include `-nh` (no hardware configuration) `-nv` (no video configuration). Only use the hardware configuration of running on the raspberry pi.
- When developing on a local machine, use the `-dev` argument to set a known MAC address (DEVELOP).

# Hardware
This software package is compatible and can be installed/ran on linux/unix based machines.
It is specifically designed for the raspberry pi. The hardware components listed below should be connected to the raspberry 
pi when running in production mode. For each component, the associated gpio pin is included and how to connect it.

### GPS Breakout Sensor
- Connected via `usb to serial` adapter
- Connection diagram can be found at the following link:

  - https://learn.adafruit.com/adafruit-ultimate-gps-on-the-raspberry-pi?view=all
  
### Temperature Sensor
- Connected via `GPIO: 4`
- a `4.7k ohm resistor` is needed between the `VCC` and `DATA` lines

### Motion (PIR) sensor
- Connected via `GPIO: 22`

### Status LED
- Connected via `GPIO: 17`
- a `270 ohm resistor` is needed between the LED (short leg) and `GND` line

### Panic (Push) button
- Connected via `GPIO: 6`

### Vibration sensor
- Connected via `GPIO: 27`


# REST API
The server uses a REST API for system access via a client mobile app or raspberry pi client. Below are the API calls available and the required data for success responses.
Each path includes a leading string of `http://{address}:3002/path/to/route`

### Routes

1. `security/arm`
2. `security/disarm`
3. `security/false_alarm`
4. `system/location`
5. `system/temperature`
6. `system/speedometer`

# Python Details
## first time python setup
before beginning few prerequisite python packages must be installed and up to date. on macos:
```shell
$ sudo easy_install --upgrade pip virtualenv tox
```

## virtualenv
[virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) is a fantastic tools for creating python environments.

To easily create a virtualenv for development:
```shell
$ make develop
```

To easily create a virtualenv for production:
```shell
$ make prod
```
- Only use this when we test the entire system

To begin using the virtual:
```shell
$ source venv-securityserverpy/bin/activate
```

OpenCV is used for video capture. However, the installation methods are different for certain systems:

- For MacOS, use `make opencv_install_mac`
- For linux, use `make opencv_install_linux`
- Also on linux, you need to symlink opencv into the env:

```shell
$ make opencv_link_linux_pi (for ubuntu mate)
$ make opencv_link_linux_desktop (for ubuntu)
```

The packages installed into the virtualenv are dictated by two files
### `requirements/linux.txt`
### `requirements/osx.txt`
### `requirements/pi.txt`
In this file, all packages required to run the tool should be listed. Specify the exact version of the packages so that changes in dependencies don't break your tool.
### `requirements-dev.txt`
In this file, additional packages required to test the tool should be listed. Generally, the exact version is not specified.


## pre-commit
[pre-commit](http://pre-commit.com) is a tool to find and fix common issues before changes are committed. `pre-commit` will run before each `git commit`.
To run `pre-commit` on demand:
```shell
$ pre-commit run -a
```
- pre-commit is currently not being used by this program.

## running your code
Writing code is great. But running it is usually the end goal. In `setup.py` the `entry_points` section defines command-line entry points for running your code. Inside your virtualenv, run:
```shell
$ securityserverpy
```
- See the above section on required arguments to successfully run the program.

## Versioning your code
There is a single definition of the package version in `securityserver/version.py`. Updating there changes the package version.

# Testing

## running automated tests
- Test are organized using the `unittest` framework provided by python. To setup tests and successfully close them, use the `setUp` and `tearDown` methods
- Examples are in the current test files in the project.
```shell
$ make test
```
- Make sure to keep all test cases uniform.

## running automated tests with a debugger
- If you need to run test with a debugger, then use the following command:
```shell
$ make testpdb
```

## Contributing
- If you want to contribute, create a new branch and update your code. The master branch is protected, so submit a pull request and let another contributor review it.
- Before submitting PR, please make sure the program successfully runs as expected and that all tests are passing with no pollution.