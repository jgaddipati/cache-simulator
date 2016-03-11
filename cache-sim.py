# !/usr/bin/env python

'''
Author: Jagadeesh Gaddipati
Email: jgadd001@ucr.edu
'''
import sys
from cache import Cache
from trace import Trace

def main(argv):
	if len(argv) != 1:
		print "Usage:"
		print "$ python cache-sim.py <trace_file_name>"
		sys.exit()

	print "Initializing..."
	cache_sim = Cache('config')
	#cache_sim.print_config()

	try:
		with open(argv[0], "rb") as trace:
			print "Simulating..."

			for line in trace:
				words = line.split() # separate words in the line
				if words[7] == 'L':
					inst_node = {'inst' : 'LD', 'addr' : int(words[9], 16)} # reading in hex
					cache_sim.run(inst_node)
				elif words[7] == 'S':
					inst_node = {'inst' : 'ST', 'addr' : int(words[9], 16)} # reading in hex
					cache_sim.run(inst_node)
			'''
			for line in trace:
				words = line.split() # separate words in the line
				if words[0] == 'LD':
					inst_node = {'inst' : 'LD', 'addr' : int(words[2], 16)} # reading in hex
					cache_sim.run(inst_node)
				elif words[0] == 'ST':
					inst_node = {'inst' : 'ST', 'addr' : int(words[2], 16)} # reading in hex
					cache_sim.run(inst_node)
			'''
	except IOError as error:
		print '====== ERROR ====='
		print "Error opening file", error.filename
		print error.message
		sys.exit()


	"""
	print "Loading trace..."
	trace_obj = Trace(argv[0])

	print "Simulating..."
	cache_sim.run(trace_obj.trace)
	"""

	print "Finished"
	cache_sim.print_stats()


if __name__ == '__main__':
	main(sys.argv[1:])
