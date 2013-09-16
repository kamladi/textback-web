TextBack-web
============

Web Server component for TextBack: PennApps F13

Setup
------
1. Install virtualenv
```
$ sudo easy_install pip
$ sudo pip install virtualenv
$ virtualenv --distribute venv
```
2. Activate virtualenv, install dependencies
```
$ virtualenv venv/bin/activate
$ pip install -r requirements.txt
```
3. Deactivate virtual environment to setup links for Twilio libraries
```
$ deactivate
$ ln -s venv/lib/python2.7/site-packages/twilio .
$ ln -s venv/lib/python2.7/site-packages/httplib2 .
$ ln -s venv/lib/python2.7/site-packages/six.py .
```
4. Setup a Twilio developer account, and copy/paste your credentials in the appropriate places in textback.py

Running
-------

To run the app locally (e.g. for testing), download the Google App
Engine SDK from http://code.google.com/appengine/downloads.html.  You
can then run the server using

  make serve

(assuming you're on Linux or Mac OS X).  On Windows just use Google
App Engine Launcher.
