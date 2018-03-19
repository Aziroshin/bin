#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import sys
import time
import json
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
	def __init__(self, beginning=0, end=0):
		self.filledOrders = []
		self._beginning = beginning
		self._end = end
		
	@property
	def beginning(self):
		"""UNIX timestamp of the second denoting the beginning of this window."""
		if self._beginning == 0:
			raise MarketHistoryTimeWindowTimestampsUninitializedError()
		else:
			return self._beginning
		
	@beginning.setter
	def beginning(self, timestamp):
		self._beginning = timestamp
		
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
		return True if self._beginning > timestamp else False
	
	def encompasses(self, timestamp):
		"""Returns True if the specified timestamp is encompased by this time window, False otherwise."""
		return True if not self.olderThan(timestamp) and not self.newerThan(timestamp) else False
		
	def adjust(self, timestamp):
		"""Expands the time window if it doesn't yet encompass the specified timestamp."""
		if self.olderThan(timestamp):
			self.end = timestamp
		elif self.newerThan(timestamp):
			self.beginning = timestamp
		elif self._beginning == 0: # Not initialized yet - it's time to do that now.
			self.beginning = timestamp
		else:
			dprint("We should never get here.")
		
	def addFilledOrder(self, order, timestamp=None):
		"""Add a filled order that belongs to this time window."""
		self.filledOrders.append(order)
		if not timestamp == None:
			self.adjust(timestamp)

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
	def inSeconds(self):
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
	def inMinutes(self):
		"""Returns a list of time window objects with each spanning one minute of the history."""
		currentMinute = self.filledOrders[0]
		
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
			self.refresh()
	
	def refreshCache(self):
		if self.cacheFile.secondsSinceLastModification > self.updateInterval\
		or self.cacheFile.read() == "":
			if self.cacheFile.writable:
				dprint("Refreshing data.")
				self.cacheFile.write(urlopen(Request(self.address)).read().decode())
				dprint("Done refreshing data.")
	
	def refresh(self):
		self.refreshCache()
		self.string = self.cacheFile.read()
		self.dict = json.loads(self.string)

if __name__ == "__main__":

	for symbol in symbols:
		data = Data(\
			address="https://www.cryptopia.co.nz/api/GetMarketHistory/{symbol}_BTC/"\
				.format(symbol=symbol),\
			storePath=os.path.join(defaultMarketscannersDirPath, "{0}".format(symbol)),\
			updateInterval=defaultUpdateInterval)
	for window in MarketHistory(data.dict["Data"]).inSeconds:
		for order in window.filledOrders:
			#dprint("Filled order [{begin}:{end}] timestamp: {timestamp}"\
			#	.format(timestamp=order.data["Timestamp"], begin=window._beginning, end=window._end))
			pass