#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================
#==========================================================
#=============================

import matplotlib

#=======================================================================================
# Imports
#=======================================================================================

class OhlcGraph(object):
	def __init__(self, pandasOhlcObject, title=""):
		"""Takes resample().ohlc data from a DataFrame and displays a graph window.
		self.pohlc holds the data as provided in pandas ohlc form.
		self.mohlc holds the transformed, matplotlib friendly form of the data."""
		
		# This is just for wild testing purposes.
		# Right now, I need something to visualize the data fast for debugging.
		# This will (have to) do. Zero code quality guaranteed.
		
		self.pohlc = pandasOhlcObject
		self.mohlc = self.pohlcToMohlc(self.pohlc)
		self.figure = matplotlib.pyplot.figure()
		self.plot = pyplot.subplot2grid((1,1,), (0,0))
		
		#=============================
		# Set up.
		#=============================
		# Adaption of the matplotlib example found on:
		#     https://pythonprogramming.net/candlestick-ohlc-graph-matplotlib-tutorial/
		
		x = 0
		y = len(self.mohlc)
		
		matplotlib.candlestick_ohlc(self.plot, self.mohlc, width=0.4,\
			colorup="#77d879", colordown="#db3f3f")
		
		for label in self.plot.xaxis.get_ticklabels():
			label.set_rotation(45)
			
		self.plot.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y-%m-%d"))
		self.plot.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(10))
		self.plot.grid(True)
		
		matplotlib.pyplot.xlabel("Date & Time")
		matplotlib.pyplot.ylabel("Price")
		matplotlib.pyplot.title(title)
		matplotlib.pyplot.subplots_adjust(let=0.9, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)
		matplotlib.pyplot.legend()
		
	def pohlcToMohlc(self, pohlc):
		"""Takes panda OHLC object (pohlc) and returns matplotlib friendly OHLC object (mohlc)."""
		mohlc = []
		rowIndex = 0
		while rowIndex < len(pohlc.index):
			mohlc.append((pohlc.index, pohlc.open, pohlc.high, pohlc.low, pohlc.close))
			rowIndex += 1
		return mohlc
	
	def show(self):
		pyplot.show()