#!/usr/bin/python	

from lcd import LCD
from radio import Radio
from mpd import MPDClient
from time import sleep
from quick2wire.gpio import pins, In, Both, Rising, PullUp
import _thread
import select

def updateTrackData():
	while True:
		metadata = radio.selectTrackUpdate()

		if ("name" in metadata):
			display.display(metadata["name"], 1)
 
		if ("title" in metadata):
			display.display(metadata["title"], 3)

def watchInputDevices():
	rotaryA = pins.pin(7, direction=In, interrupt=Both, pull=PullUp)
	rotaryB = pins.pin(0, direction=In, interrupt=Both, pull=PullUp)
	switch = pins.pin(2, direction=In, interrupt=Rising, pull=PullUp)
	
	with rotaryA, rotaryB, switch:
		lastActive = "a"
		epoll = select.epoll()
		epoll.register(rotaryA, select.EPOLLIN|select.EPOLLET)
		epoll.register(rotaryB, select.EPOLLIN|select.EPOLLET)
		epoll.register(switch, select.EPOLLIN|select.EPOLLET)
		sleep(1)
		while True:
			events = epoll.poll()
			for fileno, event in events:
				if fileno == switch.fileno():
					print("SWITCH PRESSED")
				else:
					a = rotaryA.value
					b = rotaryB.value
					if (a == 0) and (b == 1):
						lastActive = "b"
					elif (b == 0) and (a == 1):
						lastActive = "a"
	
					elif (a == b == 1):
						display.loading()
						if lastActive == "a":
							radio.prev()
						else:
							radio.next()


display = LCD()
radio = Radio()


trackDataThread = _thread.start_new_thread(updateTrackData, ())
watchInputDevices()

radio.shutdown()
