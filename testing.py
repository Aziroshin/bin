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

import argparse
import os

#=======================================================================================
# Configuration
#=======================================================================================

#=======================================================================================
# Library
#=======================================================================================

#=======================================================================================
# Action
#=======================================================================================

if __name__ == "__main__":
	
	#==========================================================
	# Arguments
	#==========================================================
	argparser = argparse.arg_parser()
	
	# We take a single argument (besides argparse defaults, of course): Name of the testing module to load.
	# Upon calling --help, we'll also list all the available modules from the testing directory.
	argparser.add_argument(\
		"module", help="Name of the testing module to run. Consult contents of the"
		" testing dir for options:{dirContents}"\
			.format(dirContents=\
				[module.rpartition(".")[0] for module in os.listdir(os.path.join(__file__, "testing"))\
					if not module == "__init__.py"
				]
			)
		)
			
	args = argparser.parse_args()

	chosenModule = __import__("testing.{moduleName}".format(moduleName=args.module))