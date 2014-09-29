import select
import multiprocessing
from gpio import Pin, In, Out, Falling, PullUp

class Button:
	def __init__(self, buttonPinNumber, buttonPinName, pullupPinNumber, pullupPinName, callback):
		self.button = Pin(buttonPinNumber, direction=In, interrupt=Falling, pull=PullUp, suffix="_"+buttonPinName)
		self.pullup = Pin(pullupPinNumber, direction=Out, suffix="_"+pullupPinName)
		self.epoll = select.epoll()
		self.callback = callback
		
	def run(self):
		with self.button, self.pullup:
			self.pullup._write("value", "1")
			self.epoll.register(self.button, select.EPOLLIN|select.EPOLLET)
			while True:
				events = self.epoll.poll()
				self.processEvents(events)

	def processEvents(self, events):
		for fileno, event in events:
			if (fileno == self.button.fileno()) and (self.button.value == 0):
				self.callback()
	
	def enable(self):
		self.worker = multiprocessing.Process(target=self.run)
		self.worker.start()

	def disable(self):
		print("Not implemented")
