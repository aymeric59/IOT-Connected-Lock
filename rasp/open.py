#!/usr/bin/env python3.5
#-*- coding: utf-8 -*-
import RPi.GPIO as GPIO
from pirc522 import RFID
import time, telegram
import requests


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

LED_R = 7
LED_G = 11

def SetAngle(angle) :

	duty = angle / 18 + 2

	GPIO.setup(3, GPIO.OUT)
	GPIO.output(3, True)

	pwm = GPIO.PWM(3, 50)
	pwm.start(0)
	pwm.ChangeDutyCycle(duty)

	time.sleep(1)	
	GPIO.output(3, False)
	pwm.ChangeDutyCycle(0)


def rotate() :

	SetAngle(90)
	time.sleep(5)
	SetAngle(0)


def turn_high (gpio) :
	GPIO.setup(gpio, GPIO.OUT)
	GPIO.output(gpio, GPIO.HIGH)

def turn_low (gpio) :
	GPIO.setup(gpio, GPIO.OUT)
	GPIO.output(gpio, GPIO.LOW)

def sendTelegramMessage () :
	bot = telegram.Bot(token='590915343:AAGYJp3CDm2FRvKZ4Rpi37wRk3XtkVSehW4')
	bot.send_message(chat_id='599439771', text="Vous vous êtes bien connecté !")
	bot.send_message(chat_id='446171376', text="Vous vous êtes bien connecté !")

rc522 = RFID()
turn_low(LED_G)
turn_low(LED_R)

while True :
	rc522.wait_for_tag()
	(error, tag_type) = rc522.request()

	if not error :
		(error, uid) = rc522.anticoll()

		if not error :
			
			badge_uid = ''.join([str(x) for x in uid])

			result = requests.get('https://f1b7ee9b.ngrok.io/open/'+str(badge_uid), auth=("11", "VHw10LEyDytntUPUZV2GfA7bANJ4yWySo79Kbo6SIcApk81y")).json()

			if result["success"] :

				status = 1
				turn_high(LED_G)
				print("Bien connecté !")
				rotate()
				turn_low(LED_G)


			else :

				status = 0
				print("Entrée interdite !")
				turn_high(LED_R)
				time.sleep(2)
				turn_low(LED_R)


			requests.get('https://f1b7ee9b.ngrok.io/send_log/'+str(badge_uid)+'/'+str(status), auth=("11", "VHw10LEyDytntUPUZV2GfA7bANJ4yWySo79Kbo6SIcApk81y")).json()





			
