#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""Runs testing modules from the testing directory. Not to confuse with unit tests."""
# Convention: "tests" like these will be called "testings" throughout the codebase.
# "testings" are everything test related that doesn't fit the unit test paradigm,
# typically geared towards analyzing what's appening in the application for development
# and debugging purposes.

#=======================================================================================
# Imports
#=======================================================================================
#==========================================================
#=============================

from pathlib import Path
import argparse
import os
import sys

#=======================================================================================
# Configuration
#=======================================================================================

#=======================================================================================
# Library
#=======================================================================================

#=============================
# Arguments
#=============================

class Arguments(object):
	
	#=============================
	"""A basic class for the setup for the arguments we take. Override .setUp() to implement."""
	#=============================
	
	def __init__(self):
		self.parser = argparse.ArgumentParser()
		self.setUp()
		
	def setUp(self):
		"""Override this with your particular argument configuration."""
		pass
	
	def get(self):
		"""Get the initialized argparse.Namespace object for our arguments."""
		return self.parser.parse_args()
	
class TestingArguments(Arguments):
	
	#=============================
	"""A basic class for the setup for the arguments we take. Override .setUp() to implement."""
	#=============================
	
	def setUp(self):
		
		""" We take a single argument besides argparse's defaults: Name of the testing module to load.
		Upon calling --help, we'll also list all the available modules from the testing directory."""
		
		# Absolute path to our script.
		excDirPath = os.path.join(Path(__file__).absolute().parent.as_posix())
						 
		self.parser.add_argument(\
			"module", help="Name of the testing module to run. Consult contents of the"
			" testing dir for options: {dirContents}"\
				.format(dirContents=\
					", ".join(\
						[fileName.rpartition(".")[0]\
							for fileName in os.listdir(os.path.join(excDirPath, "testings"))\
							if not fileName == "__init__.py"\
							or not Path(os.path.join(excDirPath, fileName)).is_dir\
						]
					)
				)
			)

#=======================================================================================
# Action
#=======================================================================================

if __name__ == "__main__":
	
	args = TestingArguments().get()
	import simplecryptopiascanner

	chosenModule = __import__(name="testings.{moduleName}".format(moduleName=args.module),\
		globals=globals(), locals=locals(), fromlist=[args.module], level=0)
	chosenModule.Testing().run()