from collections import namedtuple
import inspect
import time

Run = namedtuple("Run", ["problem", "factor", "time"])

class Bench(object):
	
	"""Takes a list of functions to benchmark.
	Each function has to return two values: start and end time.
	
	Objects of this class feature a .string method, which is returned for
	__repr__() and __str__() and contains a summary of all functions
	specified in the list, containing the following information:
		[function name]
			The factor as to how much faster or slower it ran than the initial function.
			The fastest execution time of the function as determined by multiple iterations.
	
	Parameters:
		
		problems (list): Default: []
			The list of functions to benchmark.
		
		run (bool): Default: True
			Whether to run the benchmark at the end of the constructor.
		
		iterations (int): Default: 10
			How many times to repeat a function before min() is used on a list of all
			time values gathered through that to determine its best time.
		
		howMuchFaster (bool): Default: True
			If True, factor values will be calculated and presented under the assumption
			that we want to know how much faster all the other functions in the list
			are performing in comparison to the first function in the list (higher values mean faster).
			If False, it'll be assumed that we want to know how much slower their
			performance is (higher values mean slower).
		
		factorRoundingPrecision(None or int): Defalut: None
			To which digit the comparison factor is to be rounded.
			If None, no rounding happens.
			Is overridden by factorAsInt (if that one is True, it'll have no decimals).
			
		factorAsInt(bool): Default: False
			Whether the factor is to be typecasted to int().
			If True, will override factorRoundingPrecision."""
	
	def __init__(self, problems=[], run=True, iterations=10, howMuchFaster=True,\
	factorRoundingPrecision=None, factorAsInt=False):
		
		# Declarations & defaults.
		self.runs = [] # List of Result type namedtuples.
		self.baseTime = None
		
		# Data.
		self.problems = problems
		
		# Settings.
		self.iterations = iterations
		self.howMuchFaster = howMuchFaster
		self.factorRoundingPrecision = factorRoundingPrecision
		self.factorAsInt = factorAsInt
		self.factorStrings = {True: "Faster by", False: "Slower by"}
		
		# Run immediately if specified.
		if run == True:
			self.run(problems=self.problems)
	
	def __repr__(self):
		return self.string
	
	def __str__(self):
		return self.string
	
	def getRoundedFactor(self, factor):
		if self.factorAsInt:
			return int(factor)
		if not self.factorRoundingPrecision == None:
			return round(factor, self.factorRoundingPrecision)
		return factor
	
	@property
	def string(self):
		return "\n".join(\
			["[{problem}] \n\t{factorString}: {factor}\n\ttime: {time}"\
				.format(problem=run.problem.__name__,\
					factor=self.getRoundedFactor(run.factor),\
					factorString=self.factorStrings[self.howMuchFaster], time=run.time)\
				for run in self.runs\
			])
	
	def run(self, problems=None, iterations=None):
		
		"""Run a list of functions, adding the time it took to run it to self.runs.time."""
		
		if problems == None: problems = self.problems
		if iterations == None: iterations = self.iterations
		
		for problem in problems:
			times = []
			count = 0
			for pausedIteration in range(0, iterations):
				print("=== [Start] {0}".format(problem.__name__))
				start, end = problem()
				times.append(end-start)
				print("=== [End] {0}".format(problem.__name__))
				count += 1
			time = min(times)
			self.runs.append(Run( problem, self.getFactor(time), time ))
			
	def getFactor(self, time):
		
		"""Get the comparison factor based on howMuchFaster.
		If howMuchFaster is True, it'll divide the time of the first function by
		the time specified for this function. If it's False, it'll do vice versa.
		
		That results in the first function always getting a factor of 1."""
		
		if self.baseTime == None:
			self.baseTime = time
		
		if self.howMuchFaster:
			return self.baseTime / time
		
		return time / self.baseTime