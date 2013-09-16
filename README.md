TextBack-web
============
Web Server component for TextBack: PennApps F13.

Link for the Android app repo:
https://github.com/kamladi/TextBack-android

TextBack is an Android(4.0+) app that texts for you when you can't. It's essentially an e-mail autoresponder, except for SMS messages.
You can create custom messages to send or use predefined templates. TextBack also has an optional web component that allows you
to start the app remotely from a web interface. This is especially helpful if you left your phone at home/can't find it.
Start textback remotely and stop worrying about not responding to SMSs from friends/colleagues.

Video
--------
A crude video of it in action: http://pennapps.challengepost.com/submissions/17082-textback

Caveats
--------

Though TextBack responds to SMS messages, those messages don't show up in your conversation list.
It's on the list of things we want to add, but couldn't figure it out.

Setup
------
1. Install virtualenv
```
sudo easy_install pip
sudo pip install virtualenv
virtualenv --distribute venv
```
2. Activate virtualenv, install dependencies
```
virtualenv venv/bin/activate
pip install -r requirements.txt
```
3. Deactivate virtual environment to setup links for Twilio libraries
```
deactivate
ln -s venv/lib/python2.7/site-packages/twilio .
ln -s venv/lib/python2.7/site-packages/httplib2 .
ln -s venv/lib/python2.7/site-packages/six.py .
```
4. Setup a Twilio developer account, and copy/paste your credentials in the appropriate places in textback.py

Running
-------

To run the app locally (e.g. for testing), download the Google App
Engine SDK from http://code.google.com/appengine/downloads.html.

About
=====

TextBack was written for the Fall 2013 Pennapps Hackathon by:

* Dan Yang [(dsyang)](https://github.com/dsyang)
* Kedar Amladi [(kamladi)](https://github.com/kamladi)
* Shubit Singh [(shubhitms)](https://github.com/shubhitms)
* Adhish Ramkumar [(diseldeesh)](https://github.com/dieseldeesh)
