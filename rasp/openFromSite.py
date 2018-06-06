#!/usr/bin/env python3.5
#-*- coding: utf-8 -*-
import RPi.GPIO as GPIO
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

	SetAngle(180)
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

turn_low(LED_G)
turn_low(LED_R)

turn_high(LED_G)
print("Bien connecté !")
rotate()
turn_low(LED_G)
			
			

			
