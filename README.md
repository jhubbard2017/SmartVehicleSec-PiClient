# Smart Vehicle Security Server
Python server software for the Smart Vehicle Security System.

## Usage Examples
### running on local machine and raspberry pi
- this example assumes a python virtual env has already been established - see details on virtual env
- this example does not trigger any calls to hardware devices
```shell
(venv-securityserverpy) $ securityserverpy -i ip_address -p port 
```
- the required arguments are the ip address and port number. These two need to be specified to start the program.
- Optional arguments include `-nh` (no hardware configuration) `-nv` (no video configuration). Only use the hardware configuration of running on the raspberry pi.

# YAML Configurations

## Security Config File
`securityserverpy` uses a yaml security config file:
```shell
yamls/serverconfig.yaml
```

### Config Values
- `system_armed` security system is armed
- `system_breached` security system has been breached
- `cameras_live` cameras are currently live and/or recording

## Devices File
`securityserverpy` uses a yaml devices file. to create a device file:
```shell
yamls/devices.yaml
```

### Devices Values
For flexibility purposes, users may be able to connect more than one device/client to our security server.
- `devices` list of connected and allowed devices

## Logs File
- user controlled and security controlled alerts/logs are store in a logs config file:
```shell
yamls/logs.yaml
```

### Logs Values
- `user_controlled_type` logs initiated/created by the client
- `security_controlled_type` logs initiated/create by the security system

## Contacts File
`securityserverpy` uses a yaml contacts file for storing the trustworthy contacts of the client:
```shell
yamls/contacts.yaml
```

### Contacts Values
- `contacts` list of dict objects representing a contact (name, phone, email)

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

## specifying yaml files
- There are a group of yaml testing files in `tests/data`. If you need to add a yaml config file, you can store it in this location.
- To ensure the automated tests run smoothly and do not create any pollution, make sure you clear the associated yaml config file before and after tests.

## running automated tests
- Test are organized using the `unittest` framework provided by python. To setup tests and successfully close them, use the `setUp` and `tearDown` methods
- Examples are in the current test files in the project.
```shell
$ make test
```

## running automated tests with a debugger
- If you need to run test with a debugger, then use the following command:
```shell
$ make testpdb
```

## Contributing
- If you want to contribute, create a new branch and update your code. The master branch is protected, so submit a pull request and let another contributor review it.
- Before submitting PR, please make sure the program successfully runs as expected and that all tests are passing and not polluting.