# -*- coding: utf-8 -*-

from time import sleep
import re
from quick2wire.i2c import I2CMaster, writing
import unicodedata

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

EMPTYLINE = "                    "

class LCD(object):
	def __init__(self):
		self.write(0x03)
		self.write(0x03)
		self.write(0x03)
		self.write(0x02)
		
		self.write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
		self.write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
		self.write(LCD_CLEARDISPLAY)   
		self.write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
		sleep(0.2)   

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
		string = self.sanitise(string)

		if line == 1:
			if (len(string) > 20) and (string[19] != ' '):
				string = string[:19] + "-" + string[19:]
			self.display(string[20:],2)
			self.write(0x80)
		if line == 2:
			self.write(0xC0)
		if line == 3:
			self.display(string[20:],4)
			self.write(0x94)
		if line == 4:
			if len(string) == 20:
				string[19] = "."
				string[18] = "."
				string[17] = "."
			self.write(0xD4)

		
		if (len(string) > 20):
			string = string[:20]
		if (len(string) < 20):
			string = string + EMPTYLINE[:20-len(string)]

		for char in string:
			self.write(ord(char), Rs)
	
	def clear(self):
		self.write(LCD_CLEARDISPLAY)
		self.write(LCD_RETURNHOME)

	def disable(self):
		self.device.writeRaw(LCD_NOBACKLIGHT)

	def enable(self):
		self.device.writeRaw(LCD_BACKLIGHT)
