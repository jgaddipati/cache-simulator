# !/usr/bin/env python

'''
Author: Jagadeesh Gaddipati
SID: 861196271
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
	print "Starting...."
	cache = Cache('config')
	trace = Trace(argv[1])


if __name__ == '__main__':
	main(sys.argv[1:])