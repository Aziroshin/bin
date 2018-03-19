#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import sys
import time
import json
from urllib.request import Request, urlopen

#==========================================================
# Configuration
#==========================================================

marketscannersDirPath=os.path.join(os.path.expanduser("~"), ".local", "marketscanners")
dataStoreFilePath=os.path.join(marketscannersDirPath, "nebliopricedisplay")
coin = "NEBL"
defaultUpdateInterval = 360 # In seconds.

#==========================================================
# Library
#==========================================================

#==========================================================
class File(object):
	
	#=============================
	"""Basic file wrapper.
	Abstracts away basic operations such as read, write, etc."""
	#TODO: Make file operations safer and failures more verbose with some checks & exceptions.
	#=============================
	
	def __init__(self, path, make=False, makeDirs=False, runSetup=True):
		if runSetup:
			self.setUp(path, make, makeDirs)
	
	def setUp(self, path, make=False, makeDirs=False):
		"""Initialize the file. This can be called subsequently to reset which file is being handled."""
		self.path = path
		if not type(self.path) == str:
			raise FileError("Tried to initialize file with non-string path: {path}".format(path=self.path),\
				FileError.codes.INVALID_PATH)
		self.dirPath, self.name = self.path.rpartition(os.sep)[0::2]
		if make:
			if not self.exists:
				self.make(makeDirs=makeDirs)
		
	@property
	def lastModified(self):
		return int(os.path.getmtime(self.path))
	
	@property
	def secondsSinceLastModification(self):
		return int(time.time()) - int(self.lastModified)
	
	@property
	def exists(self):
		return os.path.exists(self.path)
	
	@property
	def dirExists(self):
		return os.path.exists(self.dirPath)
	
	@property
	def size(self):
		return os.path.getsize(self.path)
	
	def overwrite(self, data):
		with open(self.path, "w") as fileHandler:
			fileHandler.write(data)
			
	def append(self, data):
		with open(self.path, "a") as fileHandler:
			fileHandler.write(data)
	
	def read(self):
		with open(self.path, "r") as fileHandler:
			return fileHandler.read()
	
	def write(self, data):
		with open(self.path, "w") as fileHandler:
			fileHandler.write(str(data))
	
	def delete(self):
		"""Deletes the file from the filesystem."""
		os.remove(self.path)
	
	def wipe(self):
		"""Wipes the content of the file, making it empty."""
		self.overwrite("")
		
	def move(self, newPath):
		"""Moves the file to a new path."""
		if os.path.isdir(newPath):
			os.rename(self.path, os.path.join(newPath, self.name))
		else:
			os.rename(self.path, newPath)
		self.setUp(newPath)
	
	def copy(self, destPath):
		"""Copy this file to another path."""
		shutil.copy(self.path, destPath)
	
	def rename(self, newName):
		"""Rename the file (this doesn't change the location of the file, just the name)."""
		self.move(os.path.join(self.dirPath, newName))
	
	def make(self, makeDirs=False):
		"""Write empty file to make sure it exists."""
		if not self.exists:
			if makeDirs:
				if not self.dirExists:
					os.makedirs(self.dirPath)
			self.overwrite("")

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
		if self.cacheFile.secondsSinceLastModification > self.updateInterval:
			
			self.cacheFile.write(urlopen(Request(self.address)).read().decode())
	
	def refresh(self):
		self.refreshCache()
		self.string = self.cacheFile.read()
		self.dict = json.loads(self.string)
		

if __name__ == "__main__":

	data = Data("https://www.cryptopia.co.nz/api/GetMarketHistory/{coin}_BTC/".format(coin=coin),\
		dataStoreFilePath, defaultUpdateInterval)
	data.