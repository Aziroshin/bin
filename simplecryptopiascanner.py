#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================
#==========================================================
#=============================

#=============================
# Builtins.
import os
import sys
import time
import json
from urllib.request import Request, urlopen

#=============================
# Third party.
import arrow
import numpy as np
import pandas as pd
import matplotlib.pyplot as pyplot
# Kivy
import kivy
import kivy.app
# https://github.com/kivy-garden/garden.matplotlib
# Could also be obtained through garden install matplotlib
# Might fancy just linking the repository to make deployment less of a clusterfudge.
from kivy.garden.matplotlib import FigureCanvasKivyAgg

#=============================
# Internal.
from lib.azirolib.filemanagement import File
from lib.azirolib.debugging import dprint

#=======================================================================================
# Configuration
#=======================================================================================

symbols = ["NEBL"]
defaultMarketscannersDirPath=os.path.join(os.path.expanduser("~"), ".cache", "simplecryptopiascanner")
defaultUpdateInterval = 360 # In seconds.

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
# Errors
#==========================================================

class MarketHistoryTimeWindowTimestampsUninitializedError(Exception):
	pass
class MarketHistoryTimeWindowError(Exception):
	pass
class MarketHistoryTimeWindowOrderOutOfBoundsError(Exception):
	pass

#==========================================================
# GUI Classes
#==========================================================

class Gui(kivy.app.App):
	pass

#==========================================================
# API Neutral Classes
#==========================================================
# These represent inner workings and expectations of this 
# software, and should not need changing upon implementing
# a new API.

class FilledOrder(object):
	"""Represents a filled order in the market history.
	Models the data from the GetMarketHistory API call."""
	
	def __init__(self, timestamp, data):
		# We are getting the timestamp here because we need it, and we
		# want this class to be API neutral.
		self.timestamp = timestamp
		self.data = data

class Datetime(arrow.Arrow):
	"""Represents a date and time in various formats.
	Takes a UNIX timestamp for the constructor."""
	#def __init__(self):
		#self.timestamp = timestamp
		#self.datetime = arrow.fromtimestamp(self.timestamp)
		#self.iso8601 = self.arrow.strftime("%Y-%m-%dT%H-%M-%S")
		#self.humanReadable = self.arrow.strftime("%H:%M:%S, %Y-%m-%d")
		#self.microsecond = arrow.microsecond
		#self.second = self.arrow.second
		#self.minute = self.arrow.minute
		#self.hour = self.arrow.hour
		#self.day = self.arrow.day
		#self.month = self.arrow.month
		#self.year = self.arrow.year
		
	@property
	def iso8601(self):
		return self.strftime("%Y-%m-%dT%H-%M-%S")
	
	@property
	def humanReadable(self):
		return self.strftime("%H:%M:%S, %Y-%m-%d")
		
	@property
	def nextSecondBegin(self):
		"""Return Datetime object shifted to the next second, zero microseconds."""
		return self.getShifted(second=self.second+1, microsecond=0)
		
	@property
	def nextMinuteBegin(self):
		"""Return Datetime object shifted to the next minute, zero seconds and zero microseconds."""
		
		
	@property
	def nextSecond(self):
		return self.replace(second=self.second+1, microsecond=0)
		
	@property
	def nextMinute(self):
		return self.replace(minute=self.minute+1, second=0, microsecond=0)

class MarketHistoryTimeWindow(object):
	"""Groups filled orders of a specified time window of the market history together."""
	def __init__(self, begin=0, end=0):
		self.filledOrders = []
		self._begin = begin
		self._end = end
		
	@property
	def begin(self):
		"""UNIX timestamp of the second denoting the begin of this window."""
		if self._begin == 0:
			raise MarketHistoryTimeWindowTimestampsUninitializedError()
		else:
			return Datetime(self._begin)
		
	@begin.setter
	def begin(self, timestamp):
		self._begin = timestamp
		
	@property
	def end(self):
		"""UNIX timestamp of the second denoting the end of this window."""
		if self._end == 0:
			raise MarketHistoryTimeWindowTimestampsUninitializedError()
		else:
			return Datetime(self._end)
	
	@end.setter
	def end(self, timestamp):
		self._end = timestamp
		
	def olderThan(self, timestamp):
		"""Returns True if this time window is older than the specified timestamp, False otherwise."""
		return True if self._end < timestamp else False
	
	def newerThan(self, timestamp):
		"""Returns True if this time window is newer than the specified timestamp, False otherwise."""
		return True if self._begin > timestamp else False
	
	def encompasses(self, timestamp):
		"""Returns True if the specified timestamp is encompased by this time window, False otherwise."""
		return True if not self.olderThan(timestamp) and not self.newerThan(timestamp) else False
		
	def adjust(self, timestamp):
		"""Expands the time window if it doesn't yet encompass the specified timestamp."""
		if self.olderThan(timestamp):
			self.end = timestamp
		if self.newerThan(timestamp):
			self.begin = timestamp
		if self._begin == 0: # Not initialized yet - it's time to do that now.
			self.begin = timestamp
			#NOTE: Debugging.
			#dprint("We should never get here. timestamp: {timestamp}, window: {begin}::{end}"\
				#.format(timestamp=timestamp, begin=self._begin, end=self._end))
			#if not self._begin == self._end and not (self._begin == 0 or self._end == 0):
				#dprint("Wide time window: timestamp: {timestamp}, window: {begin}::{end}"\
				#.format(timestamp=timestamp, begin=self._begin, end=self._end)) # Impossible.
		
	def addFilledOrder(self, order, timestamp=None):
		
		"""Add a filled order that belongs to this time window.
		If a timestamp is specified, the window is expanded accordingly.
		
		Important: The expectation is that, if no timestamp is specified, that the window
		beginning and end have already been configured through the constructor, or are
		configured by other means. They're NOT supposed to be left unconfigured at all. """
		
		if not timestamp == None:
			self.adjust(timestamp)
		elif not self.encompasses(order.timestamp):
			raise MarketHistoryTimeWindowOrderOutOfBoundsError(\
				"Tried to add a filled order with timestamp {timestamp}, which is outside our window: {begin}:{end}"\
					.format(timestamp=order.timestamp, begin=self.begin.timestamp, end=self.end.timestamp))
		self.filledOrders.append(order)
			
	def addWindow(self, window, adjust=True):
		"""Takes another MarketHistoryTimeWindow and adds its .filledOrders to ours."""
		for filledOrder in window.filledOrders:
			if adjust:
				self.addFilledOrder(filledOrder, timestamp=filledOrder.timestamp)
			else:
				self.addFilledOrder(filledOrder)
		
	def absorbEncompassedWindows(self, windows):
		"""Absorbs windows from the specified list until we find a window that falls outside of our time window."""
		numberOfWindowsAbsorbed = 0
		for window in windows:
			try:
				self.addWindow(window, adjust=False)
			except:
				break
			numberOfWindowsAbsorbed += 1
		try:
			return windows[numberOfWindowsAbsorbed:]
		except IndexError: # We absorbed all of them, so there was nothing left at the next index.
			return []
		
#==========================================================
# API Specific Classes
#==========================================================
# These will have to be changed if ever a new API is to be
# implemented.

class MarketHistory(object):
	def __init__(self, filledOrdersList):
		self.filledOrders = [FilledOrder(filledOrder["Timestamp"], filledOrder)\
			for filledOrder in filledOrdersList]
	
	@property
	def in1Seconds(self):
		orders = []
		orderIndex = 0
		while orderIndex < len(self.filledOrders):
			currentSecond = self.filledOrders[orderIndex].data["Timestamp"]
			currentTimeWindow = MarketHistoryTimeWindow()
			orders.append(currentTimeWindow)
			while currentSecond == self.filledOrders[orderIndex].data["Timestamp"]:
				currentOrder = self.filledOrders[orderIndex]
				currentTimeWindow.addFilledOrder(order=currentOrder, timestamp=currentOrder.timestamp)
				orderIndex = orderIndex+1
				#dprint("index: {0}, len: {1}".format(orderIndex, len(self.filledOrders)))
				if orderIndex == len(self.filledOrders): # Not quite elegant.
					break
		return orders
	
	@property
	def in1Minutes(self):
		"""Returns the market history as a list of one-minute time windows."""
		
		# This method iterates through the list of one-second windows, always declaring a
		# "merger" window, taking note of the minute its second is associated with,
		# merging all windows it finds in subsequent iterations ("mergee windows") into that
		# window, until it encounters a window of which the second is of a different minute.
		# It then makes that window the new merger window and continues.
		# 
		# NOTE: If the data is missing data on the first minute, the first time window
		# may be an inaccurate representation of that minute of the market.
		# If this is used to draw candles in a graph, that has to be taken into account.
		
		mergedTimeWindows = []
		unmergedTimeWindows = self.in1Seconds
		unmergedTimeWindowIndex = 0
		while unmergedTimeWindowIndex < len(unmergedTimeWindows):
			currentMergerWindow = unmergedTimeWindows[unmergedTimeWindowIndex]
			mergedTimeWindows.append(currentMergerWindow)
			# We could choose either .begin or .end; In the case of .in1Seconds, they're the same.
			currentMergerMinute = currentMergerWindow.end.minute
			while True:
				# Merge subsequent windows until the minute changes.
				unmergedTimeWindowIndex += 1
				try:
					currentMergeeWindow = unmergedTimeWindows[unmergedTimeWindowIndex]
				except IndexError:
					break
				currentMergeeMinute = currentMergeeWindow.end.minute
				if currentMergerMinute == currentMergeeMinute:
					currentMergerWindow.addWindow(currentMergeeWindow)
				else:
					# The minute changed. Make this window the new merger.
					currentMergerWindow = currentMergeeWindow
					break
		return mergedTimeWindows
		
	def inMinutesDeprecated(self, minutes):
		# Is not programmed to be robust against leap seconds.
		mergedWindows = []
		if 60 % minutes == 0:
			unmergedTimeWindowIndex = 0
			unmergedTimeWindows = self.in1Minutes
			while unmergedTimeWindowIndex < len(unmergedTimeWindows):
				currentMergerWindow = unmergedTimeWindows[unmergedTimeWindowIndex]
				mergedWindows.append(currentMergerWindow)
				counter = 0
				for minute in range(0, minutes):
					dprint(minute)
					unmergedTimeWindowIndex += 1
					try:
						currentMergeeWindow = unmergedTimeWindows[unmergedTimeWindowIndex+counter]
					except IndexError:
						break
					# Are we still within the desired time window?
					try:
						currentMergerWindow.addWindow(currentMergeeWindow, adjust=False)
					except MarketHistoryTimeWindowOrderOutOfBoundsError:
						break
					counter += 1
		else:
			MarketHistoryTimeWindowError(\
				"A non-divisor of 60 has been specified as a time window: {0}".format(minutes))
		return mergedWindows
		
		def inMinutes(self, minutes):
			pass
	
#==========================================================
class Data(object):
	
	#=============================
	"""Currency data handler for getting and caching data from a web API."""
	#=============================
	
	def __init__(self, address, storePath, updateInterval=defaultUpdateInterval, startFresh=True):
		self.cacheFile = File(storePath, make=True, makeDirs=True)
		self.address = address
		self.updateInterval = updateInterval
		self.dict = {}
		self.string = ""
		if startFresh:
			self.refresh(noInit=True)
		self._initData()
	
	def _initData(self):
		"""Initialize the cacheFile data into the various data structures we use, such as .dict."""
		#NOTE: Could use some error handling in case the file is empty.
		self.string = self.cacheFile.read()
		self.dict = json.loads(self.string)
	
	def refreshCache(self):
		"""Refresh the cacheFile with data from the web API."""
		if self.cacheFile.secondsSinceLastModification > self.updateInterval\
		or self.cacheFile.read() == "":
			if self.cacheFile.writable:
				dprint("Refreshing data.")
				self.cacheFile.write(urlopen(Request(self.address)).read().decode())
				dprint("Done refreshing data.")
	
	def refresh(self, noInit=False):
		"""Have the cache file refreshed and re-initialize our data from it."""
		self.refreshCache()
		if noInit:
			self._initData()



#=======================================================================================
# Action
#=======================================================================================

if __name__ == "__main__":
	pass
