from mpd import MPDClient
from select import select
from os import system
import time


class Radio(object):
	stations = None
	mpd = None
	position = 1

	def __init__(self, stations):
		self.mpd = MPDClient()
		self.mpd.timeout = 10
		self.mpd.idletimeout = None
		self.mpd.connect("localhost", 6600)
		self.mpd.clear()
		for station in iter(stations):
			self.mpd.add(station)
		self.stations = self.mpd.playlist()
		print("Successfully loaded the following playlist:")
		print(self.mpd.playlist())
		print("-------")

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

	def shutdown(self):
		self.mpd.close()
		self.mpd.disconnect()
