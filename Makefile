.DELETE_ON_ERROR:

all:
	echo >&2 "Must specify target."

test:
	tox

testpdb:
	tox -epdb

develop:
	tox -edevelop

opencv_install_linux:
	sudo apt-get install libopencv-dev python-opencv

link_lpi:
	ln -s /usr/lib/python2.7/dist-packages/cv2.arm-linux-gnueabihf.so venv-securityclientpy/lib/python2.7/site-packages/cv2.so

make gpio:
	pip install RPi.GPIO

link_ldesktop:
	ln -s /usr/lib/python2.7/dist-packages/cv2.x86_64-linux-gnu.so venv-securityclientpy/lib/python2.7/site-packages/cv2.so

opencv_install_mac:
	pip install opencv-python

install_gpsd:
	sudo apt-get install gpsd gpsd-clients python-gps

gpsd_linux:
	cd venv-securityclientpy/lib/python2.7/site-packages/
	ln -s /usr/lib/python2.7/dist-packages/gps.so gps.so

prod:
	tox -evenv

clean:
	rm -rf build/ dist/ securityserverpy.egg-info/ .tox/ venv*/
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	find . -name '*.log' -delete

.PHONY:
	all test testpdb develop prod clean
