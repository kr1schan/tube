#!/usr/bin/python	

from lcd import LCD
from radio import Radio
from mpd import MPDClient
from time import sleep
from quick2wire.gpio import pins, In, Both, Falling, PullUp
import configparser
import _thread
import select
import math

active = False

def updateTrackData():
	while True:
		metadata = radio.selectTrackUpdate()

		if not active:
			continue

		if ("name" in metadata):
			display.display(metadata["name"], 1)
 
		if ("title" in metadata):
			display.display(metadata["title"], 3)

def watchInputDevices():
	rotaryA = pins.pin(0, direction=In, interrupt=Both, pull=PullUp)
	rotaryB = pins.pin(7, direction=In, interrupt=Both, pull=PullUp)
	switch = pins.pin(2, direction=In, interrupt=Falling, pull=PullUp)

	with rotaryA, rotaryB, switch:
		global active
		seq = (1 ^ 1) | 1 << 1
		delta = 0
		deltaaccu = 0
		epoll = select.epoll()
		epoll.register(rotaryA, select.EPOLLIN|select.EPOLLET)
		epoll.register(rotaryB, select.EPOLLIN|select.EPOLLET)
		epoll.register(switch, select.EPOLLIN|select.EPOLLET)
		while True:
			events = epoll.poll()
			for fileno, event in events:
				if fileno == switch.fileno():
					if (switch.value == 0):
						print("SWITCH PRESSED")
						if active:
							display.disable()
							radio.stop()
						else:
							display.enable()
							radio.play()
						active = not active
				else:
					a = rotaryA.value
					b = rotaryB.value
					newDelta = 0
					newseq = (a ^ b) | b << 1
					if newseq != seq:
						newDelta = (newseq - seq) % 4
						if newDelta == 3:
							newDelta = -1
						elif newDelta == 2:
							newDelta = int(math.copysign(newDelta, delta))
						delta = newDelta
						deltaaccu += delta
						if (deltaaccu >= 4):
							deltaaccu = 0
							print("NEXT")
							display.status("loading")
							radio.next()
						elif (deltaaccu <= -4):
							deltaaccu = 0
							print("PREV")
							display.status("loading")
							radio.prev()
						seq = newseq

config = configparser.ConfigParser()
config.read("tube.cfg")

display = LCD(config["display"]["address"])
display.enable()

radio = Radio(config["radio"]["stations"].splitlines())

trackDataThread = _thread.start_new_thread(updateTrackData, ())
watchInputDevices()

radio.shutdown()
