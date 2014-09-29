from mpd import MPDClient
from select import select
from os import system
import time

class Radio(object):
	stations = None
	mpd = None
	position = 1
	volume = 50

	def __init__(self, stations):
		self.mpd = MPDClient()
		self.mpd.timeout = 10
		self.mpd.idletimeout = None
		self.mpd.connect("localhost", 6600)
		self.mpd.clear()
		for station in iter(stations):
			if (station != None) and (station != ""):
				self.mpd.add(station)
		self.stations = self.mpd.playlist()
		print("Successfully loaded the following playlist:")
		print(self.stations)
		print("-------")

	def increaseVolume(self):
		if (self.volume < 100):
			self.volume = self.volume + 10
			self.setVolume()

	def decreaseVolume(self):
		if (self.volume > 0):
			self.volume = self.volume - 10
			self.setVolume()

	def setVolume(self):
		system("amixer sset 'Master' " + str(self.volume) + "%")


	def play(self):
		system("mpc play " + str(self.position))

	def stop(self):
		system("mpc stop")

	def next(self):
		self.position = self.position + 1
		if self.position > len(self.stations):
			self.position = 1
		system("mpc play " + str(self.position))

	def prev(self):
		self.position = self.position - 1
		if self.position < 1:
			self.position = len(self.stations)
		system("mpc play " + str(self.position))

	def selectTrackUpdate(self):
		self.mpd.send_idle('currentsong')
		select ([self.mpd], [], [], 10)
		self.mpd.fetch_idle()
		return self.mpd.currentsong()

	def currentStreamName(self):
		return self.streams.keys()[self.position-1]
