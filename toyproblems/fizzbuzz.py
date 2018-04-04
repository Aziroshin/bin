#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from timeit import default_timer as now
from collections import namedtuple
from toylib import Bench

def nothing():
	start = now()
	end = now()
	return start, end

def basic():
	start = now()
	for number in range(1,101):
		if number % 3 == 0: print("Fizz", end="")
		if number % 5 == 0: print("Buzz", end="")
		if not number % 3 == 0 and not number % 5 == 0: print(number)
	end = now()
	return start, end

def slightlyOptimized():
	start = now()
	for number in range(1,101):
		output = ""
		if number % 3 == 0: output += "Fizz"
		if number % 5 == 0: output += "Buzz"
		elif not number % 3 == 0 and not number % 5 == 0: output = number
		print(output)
	end = now()
	return start, end

def optimized():
	start = now()
	def fizzbuzzer(number):
		output = ""
		if number % 3 == 0: output += "Fizz"
		if number % 5 == 0: output += "Buzz"
		if not number % 3 == 0 and not number % 5 == 0: output = number
		return output
	print("\n".join([str(fizzbuzzer(number)) for number in range(1, 101)]))
	end = now()
	return start, end

def optimizedWithListOutput():
	start = now()
	def fizzbuzzer(number):
		output = ""
		if number % 3 == 0: output += "Fizz"
		if number % 5 == 0: output += "Buzz"
		if not number % 3 == 0 and not number % 5 == 0: output = number
		return output
	print([fizzbuzzer(number) for number in range(1, 101)])
	end = now()
	return start, end

def optimizedWithStrListOutput():
	start = now()
	def fizzbuzzer(number):
		output = ""
		if number % 3 == 0: output += "Fizz"
		if number % 5 == 0: output += "Buzz"
		if not number % 3 == 0 and not number % 5 == 0: output = number
		return output
	print([str(fizzbuzzer(number)) for number in range(1, 101)])
	end = now()
	return start, end

print("\n=== [Benchmark]\n{0}".format(Bench(problems=[\
		nothing, basic, slightlyOptimized, optimized, optimizedWithStrListOutput, optimizedWithListOutput\
	], iterations=100, howMuchFaster=False, factorAsInt=True).string))