#!/usr/bin/python	

from lcd import LCD
from radio import Radio
from button import Button
from rotaryEncoder import RotaryEncoder
from time import sleep
import configparser
import _thread
import select
import math
import os

def updateTrackData():
	while True:
		metadata = radio.selectTrackUpdate()
		if ("name" in metadata):
			display.display(metadata["name"], 1)
		if ("title" in metadata):
			display.display(metadata["title"], 3)

def stationCallback(direction):
	if direction == "right":
		radio.next()
	else:
		radio.prev()

def volumeCallback(direction):
	if direction == "right":
		radio.decreaseVolume()
	else:
		radio.increaseVolume()

def powerOffButtonCallback():
	radio.stop()
	display.disable()
	os.system("shutdown -h now")

config = configparser.ConfigParser()
config.read("tube.cfg")

display = LCD(config["display"]["address"])
display.enable()

radio = Radio(config["radio"]["stations"].splitlines())
trackDataThread = _thread.start_new_thread(updateTrackData, ())

powerOffButton = Button(int(config["button"]["pinNumber"]),config["button"]["pinName"],int(config["button"]["pullupNumber"]),config["button"]["pullupName"], powerOffButtonCallback)
powerOffButton.enable()

stationRotary = RotaryEncoder(int(config["rightRotary"]["aPinNumber"]),config["rightRotary"]["aPinName"],int(config["rightRotary"]["aPullupNumber"]),config["rightRotary"]["aPullupName"],int(config["rightRotary"]["bPinNumber"]),config["rightRotary"]["bPinName"],int(config["rightRotary"]["bPullupNumber"]),config["rightRotary"]["bPullupName"],stationCallback)
stationRotary.enable()

volumeRotary = RotaryEncoder(int(config["leftRotary"]["aPinNumber"]),config["leftRotary"]["aPinName"],int(config["leftRotary"]["aPullupNumber"]),config["leftRotary"]["aPullupName"],int(config["leftRotary"]["bPinNumber"]),config["leftRotary"]["bPinName"],int(config["leftRotary"]["bPullupNumber"]),config["leftRotary"]["bPullupName"],volumeCallback)
volumeRotary.enable()

radio.play()

while True:
	sleep(1000000)
