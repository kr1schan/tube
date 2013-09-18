#!/usr/bin/python	

from lcd import LCD
from radio import Radio
from mpd import MPDClient
from time import sleep
from quick2wire.gpio import pins, In, Both, PullUp
import _thread
import select

def updateTrackData():
	while True:
		metadata = radio.selectTrackUpdate()

		if ("name" in metadata):
			display.display(metadata["name"], 1)
		else:
			display.display("loading...", 1)
 
		if ("title" in metadata):
			display.display(metadata["title"], 3)
		else:
			display.display("loading...", 3) 

def watchRotaryEncoder():
	rotaryA = pins.pin(7, direction=In, interrupt=Both, pull=PullUp)
	rotaryB = pins.pin(0, direction=In, interrupt=Both, pull=PullUp)
	
	with rotaryA, rotaryB:
		last = [[1,1],[1,1]]
		lastActive = "a"
		epoll = select.epoll()
		epoll.register(rotaryA, select.EPOLLIN|select.EPOLLET)
		epoll.register(rotaryB, select.EPOLLIN|select.EPOLLET)
		while True:
			events = epoll.poll()
			for fileno, event in events:
				a = rotaryA.value
				b = rotaryB.value
				
				if (a == 0) and (b == 1):
					lastActive = "b"
				elif (b == 0) and (a == 1):
					lastActive = "a"
	
				elif (a == b == 1):
					if lastActive == "a":
						radio.prev()
					else:
						radio.next()

display = LCD()
display.display("HELLO WORLD", 1)
radio = Radio()
sleep(1)

trackDataThread = _thread.start_new_thread(updateTrackData, ())
#rotaryEncoderThread = _thread.start_new_thread(watchRotaryEncoder, ())
watchRotaryEncoder()

print("waiting for join")

#trackDataThread.join()
#rotaryEncoderThread.join()

sleep(1000)

print("should never happen")
radio.shutdown()
