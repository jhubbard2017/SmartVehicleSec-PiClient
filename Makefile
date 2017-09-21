.DELETE_ON_ERROR:

all:
	echo >&2 "Must specify target."

test:
	tox

testpdb:
	tox -epdb

develop:
	tox -edevelop

opencv:
	cd venv-securityclientpy/lib/python2.7/site-packages/
	ln -s /usr/lib/python2.7/dist-packages/cv2.arm-linux-gnueabihf.so cv2.so

prod:
	tox -evenv

clean:
	rm -rf build/ dist/ securityserverpy.egg-info/ .tox/ venv*/
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	find . -name '*.log' -delete

.PHONY:
	all test testpdb develop prod clean
