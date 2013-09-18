# -*- coding: utf-8 -*-

from time import sleep
import re
from quick2wire.i2c import I2CMaster, writing
import unicodedata
import threading

# LCD Address
ADDRESS = 0x3f

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

En = 0b00000100 # Enable bit
Rw = 0b00000010 # Read/Write bit
Rs = 0b00000001 # Register select bit

EMPTYLINE = "                   "

class LCD(object):
	active = False	
	displaySemaphore = threading.Semaphore()

	def __init__(self):
		self.write(0x03)
		self.write(0x03)
		self.write(0x03)
		self.write(0x02)
		
		self.write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
		self.write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
		self.write(LCD_CLEARDISPLAY)   
		self.write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
		sleep(1)

	def write(self, cmd, mode=0):
		self.write4BitCode(mode | (cmd & 0xF0))
		self.write4BitCode(mode | ((cmd << 4) & 0xF0))

	def write4BitCode(self, data):
		with I2CMaster() as i2c:
			i2c.transaction(writing(0x3f, [data | LCD_BACKLIGHT]))
			sleep(0.0001)
		self.lcdStrobe(data)
	
	def lcdStrobe(self, data):
		with I2CMaster() as i2c:
			i2c.transaction(writing(0x3f, [data | En | LCD_BACKLIGHT]))
			sleep(0.0005)
			i2c.transaction(writing(0x3f, [(data & ~En) | LCD_BACKLIGHT]))
			sleep(0.0001)

	def sanitise(self, string):
		sanitised = string.replace('ä', "ae")
		sanitised = sanitised.replace('ö', "oe")
		sanitised = sanitised.replace('Ã¶',"oe")
		sanitised = sanitised.replace('ü', "ue")
		sanitised = sanitised.replace('Ã¼', "ue")
		return sanitised
 
	def display(self, string, line):
		self.displaySemaphore.acquire()
		self._display(string, line)
		self.displaySemaphore.release()

	def _display(self, string, line):
		string = self.sanitise(string)

		if line == 1:
			self._wrapLine(string, line)
			self.write(0x80)
		if line == 2:
			self.write(0xC0)
		if line == 3:
			self._wrapLine(string, line)
			self.write(0x94)
		if line == 4:
			self.write(0xD4)
		
		if (len(string) < 20):
			string = string + EMPTYLINE[:20-len(string)]
		if (len(string) > 20):
			string = string[:20]

		for char in string:
			self.write(ord(char), Rs)

	def _wrapLine(self, string, line):
		if len(string) > 20:
			self._display(string[20:], line+1)
		else:
			self._display(EMPTYLINE, line+1)
	
	def clear(self):
		self.write(LCD_CLEARDISPLAY)
		self.write(LCD_RETURNHOME)

	def disable(self):	
		self.active = False
		with I2CMaster() as i2c:
			i2c.transaction(writing(0x3f, [LCD_NOBACKLIGHT]))

	def enable(self):
		self.active = True
		with I2CMaster() as i2c:
			i2c.transaction(writing(0x3f, [LCD_BACKLIGHT]))

	def loading(self):
		if self.displaySemaphore.acquire(blocking=False):
			self._display(EMPTYLINE, 1)
			self._display("       loading     ", 2)
			self._display("         ...       ", 3)
			self._display(EMPTYLINE, 4)
			self.displaySemaphore.release()	
