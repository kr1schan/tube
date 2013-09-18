from mpd import MPDClient
from select import select
from os import system
import time


class Radio(object):
	streams = None
	mpd = None
	position = 1

	def __init__(self):
		self.streams = {"WDR 5": "http://wdr5-ogg.akacast.akamaistream.net/7/232/199784/v1/gnl.akacast.akamaistream.net/wdr5-ogg", "Deutschlandfunk": "http://dradio-ogg-dlf-l.akacast.akamaistream.net/7/629/135496/v1/gnl.akacast.akamaistream.net/dradio_ogg_dlf_l"}
		self.mpd = MPDClient()
		self.mpd.timeout = 10
		self.mpd.idletimeout = None
		self.mpd.connect("localhost", 6600)
		self.mpd.clear()
		for stream in iter(self.streams):
			self.mpd.add(self.streams[stream])
		print(self.mpd.playlist())

	def play(self):
		system("mpc play " + str(self.position))

	def stop(self):
		self.mpd.stop()

	def next(self):
		self.position = self.position + 1
		if self.position > len(self.streams.keys()):
			self.position = 1
		system("mpc play " + str(self.position))

	def prev(self):
		self.position = self.position - 1
		if self.position < 1:
			self.position = len(self.streams.keys())
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
