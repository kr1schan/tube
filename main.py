#!/usr/bin/python	

from lcd import LCD
from radio import Radio
from mpd import MPDClient
from time import sleep
from quick2wire.gpio import pins, In, Both, Rising, PullUp
import _thread
import select
import math

def updateTrackData():
	while True:
		metadata = radio.selectTrackUpdate()

		if ("name" in metadata):
			display.display(metadata["name"], 1)
 
		if ("title" in metadata):
			display.display(metadata["title"], 3)

def watchInputDevices():
	rotaryA = pins.pin(0, direction=In, interrupt=Both, pull=PullUp)
	rotaryB = pins.pin(7, direction=In, interrupt=Both, pull=PullUp)
	switch = pins.pin(2, direction=In, interrupt=Rising, pull=PullUp)

	with rotaryA, rotaryB, switch:
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
					print("SWITCH PRESSED")
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
							display.loading()
							radio.next()
						elif (deltaaccu <= -4):
							deltaaccu = 0
							print("PREV")
							display.loading()
							radio.prev()
						seq = newseq

display = LCD()
radio = Radio()


trackDataThread = _thread.start_new_thread(updateTrackData, ())
watchInputDevices()

radio.shutdown()
