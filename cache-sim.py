#!/usr/bin/env python

'''
Author: Jagadeesh Gaddipati
Email: jgadd001@ucr.edu
'''

import sys
from cache import Cache
#from trace import Trace

def main(argv):
	if len(argv) != 1:
		print "Usage:"
		print "$ python cache-sim.py <trace_file_name>"
		sys.exit()

	print "Initializing Cache..."
	cache_sim = Cache('config')
	cache_sim.print_config()

	try:
		with open(argv[0], "rb") as trace:
			print "Processing Instruction Trace..."

			for line in trace:
				# handle empty lines in the trace file
				if line.strip() == '':
					continue

				words = line.split() # separate words in the line

				# if using a different trace format, just change the index and L/S format here
				# to match the Load and Store positions and address positions in the trace

				# current trace format in use:
				# words:	1  48d1e2  -1  5  45  - -  L    -264   7fffe7ff048   48d1e9   0    CMP    LOAD
				# index:    0   1       2  3  4   5 6  7      8        9          10      11   12     13

				if words[7] == 'L':
					inst_node = {'inst' : 'LD', 'addr' : int(words[9], 16)} # address is in hex, read in base 16
					cache_sim.run(inst_node)
				elif words[7] == 'S':
					inst_node = {'inst' : 'ST', 'addr' : int(words[9], 16)} # address is in hex, read in base 16
					cache_sim.run(inst_node)

	except IOError as error:
		print '====== ERROR ====='
		print "Error opening file", error.filename
		print error.message
		sys.exit()


	""" Deprecated since high memory usage with large traces (can use with small traces)
	print "Loading trace..."
	trace_obj = Trace(argv[0])

	print "Simulating..."
	cache_sim.run(trace_obj.trace)
	"""

	print "Finished"
	cache_sim.print_stats()


if __name__ == '__main__':
	main(sys.argv[1:])
