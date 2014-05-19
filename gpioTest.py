#!/usr/bin/python

import select
from gpio import Pin, In, Out, Falling, PullUp

button = Pin(60, direction=In, interrupt=Falling, pull=PullUp, suffix="_pi11")
pullup = Pin(1, direction=Out, suffix="_pg3")

with button, pullup:
	pullup._write("value", "1")
	epoll = select.epoll()
	epoll.register(button, select.EPOLLIN|select.EPOLLET)
	while True:
		events = epoll.poll()
		for fileno, event in events:
			if fileno == button.fileno():
				if (button.value == 0):
					print("PRESSED")
