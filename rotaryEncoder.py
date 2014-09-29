import select
import multiprocessing
import math
from gpio import Pin, In, Out, Both, Falling, PullUp

class RotaryEncoder:
	def __init__(self, aPinNumber, aPinName, aPullupNumber, aPullupName, bPinNumber, bPinName, bPullupNumber, bPullupName, callback):
		self.a = Pin(aPinNumber, direction=In, interrupt=Both, pull=PullUp, suffix="_"+aPinName)
		self.aPullup = Pin(aPullupNumber, direction=Out, suffix="_"+aPullupName)
		self.b = Pin(bPinNumber, direction=In, interrupt=Both, pull=PullUp, suffix="_"+bPinName)
		self.bPullup = Pin(bPullupNumber, direction=Out, suffix="_"+bPullupName)
		self.epoll = select.epoll()
		self.callback = callback
		
		self.seq = (1 ^ 1) | 1 << 1
		self.delta = 0
		self.deltaaccu = 0

	def run(self):
		with self.a, self.aPullup, self.b, self.bPullup:
			self.aPullup._write("value", "1")
			self.bPullup._write("value", "1")

			self.epoll.register(self.a, select.EPOLLIN|select.EPOLLET)
			self.epoll.register(self.b, select.EPOLLIN|select.EPOLLET)
			self.waitForInput()

	def waitForInput(self):
		while True:
			events = self.epoll.poll()
			for fileno, event in events:
				self.handleEvent(fileno, event)

	def handleEvent(self, fileno, event):
		if (fileno != self.a.fileno()) and (fileno != self.b.fileno()):
			return

		a = self.a.value
		b = self.b.value
		newDelta = 0
		newseq = (a ^ b) | b << 1

		if newseq == self.seq:
			return

		newDelta = (newseq - self.seq) % 4
		if newDelta == 3:
			newDelta = -1
		elif newDelta == 2:
			newDelta = int(math.copysign(newDelta, self.delta))
		self.delta = newDelta
		self.deltaaccu += self.delta
		if (self.deltaaccu >= 4):
			self.deltaaccu = 0
			self.callback("left")
		elif (self.deltaaccu <= -4):
			self.deltaaccu = 0
			self.callback("right")
		self.seq = newseq
	

	def enable(self):
		self.worker = multiprocessing.Process(target=self.run)
		self.worker.start()

	def disable(self):
		print("Not implemented")
