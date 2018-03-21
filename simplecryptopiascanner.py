#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import sys
import time
import json
from datetime import datetime
from lib.azirolib.filemanagement import File
from urllib.request import Request, urlopen
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
			return self._begin
		
	@begin.setter
	def begin(self, timestamp):
		self._begin = timestamp
		
	@property
	def end(self):
		"""UNIX timestamp of the second denoting the end of this window."""
		if self._end == 0:
			raise MarketHistoryTimeWindowTimestampsUninitializedError()
		else:
			return self._end
	
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
		
		self.filledOrders.append(order)
		if not timestamp == None:
			self.adjust(timestamp)
			
	def addWindow(self, window, adjust=True):
		"""Takes another MarketHistoryTimeWindow and adds its .filledOrders to ours."""
		for filledOrder in window.filledOrders:
			if adjust:
				self.addFilledOrder(filledOrder, timestamp=filledOrder.timestamp)
			else:
				self.addFilledOrder(filledOrder)

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
			currentMergerMinute = datetime.fromtimestamp(currentMergerWindow.end).minute
			while True:
				# Merge subsequent windows until the minute changes.
				unmergedTimeWindowIndex += 1
				try:
					currentMergeeWindow = unmergedTimeWindows[unmergedTimeWindowIndex]
				except IndexError:
					break
				currentMergeeMinute = datetime.fromtimestamp(currentMergeeWindow.end).minute
				if currentMergerMinute == currentMergeeMinute:
					currentMergerWindow.addWindow(currentMergeeWindow)
				else:
					# The minute changed. Make this window the new merger.
					currentMergerWindow = currentMergeeWindow
					break
		return mergedTimeWindows
	
	
	def inMinutes(self, minutes):
		# Might not be completely robust against leap seconds.
		if 60 % minutes == 0:
			while True:
				unmergedTimeWindows = self.in1Minutes
				unmergedTimeWindowIndex = 0
				counter = 0
				for count in range(0, counter):
					counter += 1
					
		else:
			MarketHistoryTimeWindowError(\
				"A non-divisor of 60 has been specified as a time window: {0}".format(minutes))
		
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

if __name__ == "__main__":
	for symbol in symbols:
		data = Data(\
			address="https://www.cryptopia.co.nz/api/GetMarketHistory/{symbol}_BTC/"\
				.format(symbol=symbol),\
			storePath=os.path.join(defaultMarketscannersDirPath, "{0}".format(symbol)),\
			updateInterval=defaultUpdateInterval,\
			startFresh=False) #NOTE: startFresh=False for debugging purposes.
	
	# Testing & Debugging
	marketHistoryIn1SecondSlices = MarketHistory(data.dict["Data"]).in1Seconds
	marketHistoryIn1MinuteSlices = MarketHistory(data.dict["Data"]).in1Minutes
	
	for window in marketHistoryIn1SecondSlices:
		for order in window.filledOrders:
			#dprint("Filled order [{begin}:{end}] timestamp: {timestamp}"\
			#	.format(timestamp=order.data["Timestamp"], begin=window._begin, end=window._end))
		
			pass
	for window in marketHistoryIn1MinuteSlices:
		print("Time window: {begin}::{end}".format(begin=window.begin, end=window.end))
		for order in window.filledOrders:
			print("\tOrder (by timestamp): {timestamp}".format(timestamp=order.timestamp))
	dprint("Filled orders found: {0}".format(len(data.dict["Data"])))
	dprint("Time windows found (.in1Seconds): {0}".format(len(marketHistoryIn1SecondSlices)))
	dprint("Time windows found (.in1Minutes): {0}".format(len(marketHistoryIn1MinuteSlices)))