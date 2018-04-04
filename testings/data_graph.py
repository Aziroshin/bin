#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================
#==========================================================
#=============================

# Builtins.
import os

# Third party.
import arrow
import pandas as pd

# Stuff particular to our testings.
from testings.utils.visualization import OhlcGraph

# A special variable SUBJECT is assigned to the module we're performing testings on.
# Chances are stuff in this section depends on module paths spoofed by the
# "testing" script upon importing this here testing module.
import simplecryptopiascanner as SUBJECT # This is the subject of our testings.

#=======================================================================================
# Configuration
#=======================================================================================

symbols = ["NEBL"]
defaultMarketscannersDirPath=os.path.join(os.path.expanduser("~"), ".cache", "simplecryptopiascanner")
defaultUpdateInterval = 360 # In seconds.

#=======================================================================================
# Library
#=======================================================================================

# This class gets instantiated by the "testing" script right after importing this module.
class Testing(object):
	def run(self):
		for symbol in symbols:
			data = SUBJECT.Data(\
				address="https://www.cryptopia.co.nz/api/GetMarketHistory/{symbol}_BTC/"\
					.format(symbol=symbol),\
				storePath=os.path.join(defaultMarketscannersDirPath, "{0}".format(symbol)),\
				updateInterval=defaultUpdateInterval,\
				startFresh=True) #NOTE: startFresh=False for debugging purposes.
		
		#=============================
		# Testing & Debugging
		#=============================
		
		startTimestamp = data.dict["Data"][len(data.dict["Data"])-1]["Timestamp"]
		endTimestamp = data.dict["Data"][0]["Timestamp"]
		start = arrow.Arrow.fromtimestamp(startTimestamp)
		end = arrow.Arrow.fromtimestamp(endTimestamp)
		
		dateRange = pd.date_range(\
			start=start.format(),\
			end=end.format(),\
			freq="min")
		
		dataFrame = pd.DataFrame(data.dict["Data"])
		dataFrame["Timestamp"] = dataFrame["Timestamp"].apply(pd.to_datetime, unit="s")
		#dprint(dataFrame["Timestamp"])
		#sys.exit()
		dataFrame = dataFrame.set_index("Timestamp")
		
		ohlc = dataFrame["Price"].resample("15min").ohlc()
		#for index in ohlc.index:
		#	dprint(index)
		
		OhlcGraph(ohlc, "Cryptopia: NEBL").show()
		
		
		
		#dprint("{startTimestamp} :: {start}, {endTimestamp} :: {end}".format(\
			#startTimestamp=startTimestamp, endTimestamp=endTimestamp, start=start, end=end))
		
		
		
		#dataFrame = pd.DataFrame(\
			#series,\
			#index=dateRange)
		
		#dprint(data.dict["Data"])
		
		
		# List methods to be tested.
		#marketHistoryIn1SecondSlices = MarketHistory(data.dict["Data"]).in1Seconds
		#marketHistoryIn1MinuteSlices = MarketHistory(data.dict["Data"]).in1Minutes
		#marketHistoryIn5MinuteSlices = MarketHistory(data.dict["Data"]).inMinutes(minutes=5)
		#marketHistoryIn15MinuteSlices = MarketHistory(data.dict["Data"]).inMinutes(minutes=15)
		#marketHistoryIn30MinuteSlices = MarketHistory(data.dict["Data"]).inMinutes(minutes=30)
		
		# .in1Seconds
		#for window in marketHistoryIn1SecondSlices:
		#	for order in window.filledOrders:
				#dprint("Filled order [{begin}:{end}] timestamp: {timestamp}"\
				#	.format(timestamp=order.data["Timestamp"], begin=window._begin, end=window._end))
		
		# .in1Minutes
		#for window in marketHistoryIn1MinuteSlices:
		#	print("Time window: {begin}::{end}".format(begin=window.begin, end=window.end))
		#	for order in window.filledOrders:
		#		print("\tOrder (by timestamp): {timestamp}".format(timestamp=order.timestamp))
		
		# .inMinutes(minutes=5)
		#for window in marketHistoryIn5MinuteSlices:
		#	print("Time window: {beginHour}:{beginMinute} -- {endHour}:{endMinute}"\
		#		.format(beginHour=window.begin.hour, beginMinute=window.begin.minute,\
		#			endHour=window.end.hour, endMinute=window.end.minute))
		#	for order in window.filledOrders:
		#		print("\tOrder (by timestamp): {timestamp}".format(timestamp=order.timestamp))
		
		# .inMinutes(minutes=15)
		#for window in marketHistoryIn15MinuteSlices:
			#if not window.begin.minute == window.end.minute:
				#print("Time window: {beginHour}:{beginMinute} -- {endHour}:{endMinute}"\
					#.format(beginHour=window.begin.hour, beginMinute=window.begin.minute,\
						#endHour=window.end.hour, endMinute=window.end.minute))
				#for order in window.filledOrders:
					#print("\tOrder (by timestamp): {timestamp}".format(timestamp=order.timestamp))
					
		# .inMinutes(minutes=30)
		#for window in marketHistoryIn30MinuteSlices:
			#if not window.begin.minute == window.end.minute:
				#print("Time window: {beginHour}:{beginMinute} -- {endHour}:{endMinute}"\
					#.format(beginHour=window.begin.hour, beginMinute=window.begin.minute,\
						#endHour=window.end.hour, endMinute=window.end.minute))
				#for order in window.filledOrders:
					#print("\tOrder (by timestamp): {timestamp}".format(timestamp=order.timestamp))
		
		# Overall respective number of windows: Number should decrease as the list goes on.
		#dprint("Filled orders found: {0}".format(len(data.dict["Data"])))
		#dprint("Time windows found (.in1Seconds): {0}".format(len(marketHistoryIn1SecondSlices)))
		#dprint("Time windows found (.in1Minutes): {0}".format(len(marketHistoryIn1MinuteSlices)))
		#dprint("Time windows found (.inMinutes(minutes=5)): {0}".format(len(marketHistoryIn5MinuteSlices)))
		#dprint("Time windows found (.inMinutes(minutes=15)): {0}".format(len(marketHistoryIn15MinuteSlices)))
		#dprint("Time windows found (.inMinutes(minutes=30)): {0}".format(len(marketHistoryIn30MinuteSlices)))
