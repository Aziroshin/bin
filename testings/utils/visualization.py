#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================
#==========================================================
#=============================

from matplotlib import pyplot as mpl_pyplot
from matplotlib import dates as mpl_dates
from matplotlib import ticker as mpl_ticker
# Installed by: pip install https://github.com/matplotlib/mpl_finance/archive/master.zip
import mpl_finance

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
		self.figure = mpl_pyplot.figure()
		self.plot = mpl_pyplot.subplot2grid((1,1,), (0,0))
		#figure, self.plot = mpl_pyplot.subplots(figsize=(10,5))
		
		#=============================
		# Set up.
		#=============================
		# Adaption of the matplotlib example found on:
		#     https://pythonprogramming.net/candlestick-ohlc-graph-matplotlib-tutorial/
		
		x = 0
		y = len(self.mohlc)
		
		#print(self.mohlc[0][0])
		#print(self.mohlc[0][1])
		#print(self.mohlc[0][2])
		#print(self.mohlc[0][3])
		#print(self.mohlc[0])
		
		mpl_finance.candlestick_ohlc(ax=self.plot, quotes=self.mohlc, width=0.005,\
			colorup="#77d879", colordown="#db3f3f")
		
		for label in self.plot.xaxis.get_ticklabels():
			label.set_rotation(90)
			
		#mpl_pyplot.xticks(self.mohlc[0])
		self.plot.xaxis.set_major_formatter(mpl_dates.DateFormatter("%Y-%m-%d"))
		#self.plot.xaxis.set_major_locator(mpl_ticker.MaxNLocator(len(self.mohlc)))
		self.plot.set_facecolor("#000000")
		self.plot.grid(True)
		
		mpl_pyplot.xlabel("Date & Time")
		mpl_pyplot.ylabel("Price")
		mpl_pyplot.title(title)
		mpl_pyplot.subplots_adjust(left=0.1, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)
		mpl_pyplot.legend()
		
	def pohlcToMohlc(self, pohlc):
		"""Takes panda OHLC object (pohlc) and returns matplotlib friendly OHLC object (mohlc)."""
		mohlc = []
		row = 0
		while row < len(pohlc.index):
			mohlc.append((mpl_dates.date2num(pohlc.index[row]), pohlc.open[row], pohlc.high[row],\
				pohlc.low[row], pohlc.close[row]))
			row += 1
		return mohlc
	
	def show(self):
		mpl_pyplot.show()
