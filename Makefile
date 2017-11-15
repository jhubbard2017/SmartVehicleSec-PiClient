.DELETE_ON_ERROR:

all:
	echo >&2 "Must specify target."

test:
	tox

testpdb:
	tox -epdb

develop_osx:
	tox -edevelop_osx

develop_linux:
	tox -edevelop_linux

develop_pi:
	tox -edevelop_pi

prod:
	tox -evenv

opencv_install_linux:
	sudo apt-get install python-opencv

install_gpsd:
	sudo apt-get install gpsd gpsd-clients python-gps

gpsd_linux:
	cd venv-securityclientpy/lib/python2.7/site-packages/
	ln -s /usr/lib/python2.7/dist-packages/gps.so gps.so

clean:
	rm -rf build/ dist/ securityserverpy.egg-info/ .tox/ venv*/
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	find . -name '*.log' -delete

.PHONY:
	all test testpdb develop prod clean
