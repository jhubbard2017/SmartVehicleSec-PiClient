# Smart Vehicle Security Server
Python client server software for the Smart Vehicle Security System (Raspberry Pi Client).

## Usage Examples
### running on local machine and raspberry pi
- this example assumes a python virtual env has already been established - see details on virtual env
- this example does not trigger any calls to hardware devices or video devices
```shell
(venv-securityclientpy) $ securityclientpy -i ip_address -p port 
```
- the required arguments are the ip address and port number. These two need to be specified to start the program.
- Optional arguments include `-nh` (no hardware configuration) `-nv` (no video configuration). Only use the hardware configuration of running on the raspberry pi.
- When developing on a local machine, use the `-dev` argument to set a known MAC address (DEVELOP).

# REST API
The server uses a REST API for system access via a client mobile app or raspberry pi client. Below are the API calls available and the required data for success responses.
Each path includes a leading string of `http://{address}:{port}/path/to/route`

### Mobile app API calls:
- `/system/arm` : arm the associated vehicle security system

  - Required data: { rd_mac_address : str }
- `/system/disarm` : disarm the associated vehicle security system

  - Required data: { rd_mac_address : str }
- `/system/false_alarm` : set a security breach as a false alarm

  - Required data: { rd_mac_address : str }
- `/system/location` : get gps location of a specific vehicle client

  - Required data: { rd_mac_address : str }
- `/system/temperature` : get temperature data of a specific vehicle client

  - Required data: { rd_mac_address : str }
- `/system/speedometer` : get speedometer data of a specific vehicle client

  - Required data: { rd_mac_address : str }
  - Returns: { speed : int, altitude : float, heading : float, climb : float }
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

The packages installed into the virtualenv are dictated by two files
### `requirements.txt`
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