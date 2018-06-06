#!/usr/bin/env python3.5
#-*- coding: utf-8 -*-
import RPi.GPIO as GPIO
from pirc522 import RFID
import time, telegram
import urllib.request
import requests
import os


os.system("kill open.py")


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

rc522 = RFID()

print("go")
rc522.wait_for_tag()
(error, tag_type) = rc522.request()

if not error :
	(error, uid) = rc522.anticoll()

	if not error :

		badge_uid = ''.join([str(x) for x in uid])

		result = requests.get('https://f1b7ee9b.ngrok.io/add_uid/'+str(badge_uid), auth=("11", "VHw10LEyDytntUPUZV2GfA7bANJ4yWySo79Kbo6SIcApk81y")).json()

		print(result['success'])

		os.system("python3.5 open.py")



			
