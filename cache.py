# !/usr/bin/env python

'''
Author: Jagadeesh Gaddipati
SID: 861196271
Email: jgadd001@ucr.edu
'''

import sys

replace_pol = {'Random' : 1, 'LRU' : 2, 'FIFO' : 3}
cache_node = {'tag' : None, 'rp_crit' : None}

class Cache(object):
	def __init__(self, block_size = 64, cache_size = 16384, assoc = 1, rp_policy = 'FIFO'):
		self.block_size = block_size
		self.cache_size = cache_size
		self.assoc = assoc
		self.sets = (cache_size / block_size) / assoc
		self.rp_policy = replace_pol[rp_policy]
		self.cache = []
		self.nread_accesses = 0
		self.nwrite_accesses = 0
		self.nread_misses = 0
		self.nwrite_misses = 0
		self.__init_cache()


	def __init_cache(self):
		if self.assoc != 0:
			for n_sets in range(self.sets):
				temp_set = []
				# for each set, there are 'assoc' number of cache lines
				for n_lines in range(self.assoc):
					temp_set.append(cache_node)
				self.cache.append(temp_set)

			#for i in range(len(self.cache)):
			#	print self.cache[i]
		else:
			print "Oops! This should not happen"
			sys.exit()
