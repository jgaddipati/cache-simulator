# !/usr/bin/env python

'''
Author: Jagadeesh Gaddipati
SID: 861196271
Email: jgadd001@ucr.edu

Notes:
Cache is arranged as a list of cache sets.
Each cache set is a list of cache_node
dictionaries. The number of cache_nodes
depend on associativity of the cache.
'''

import sys

replace_pol = {'Random' : 1, 'LRU' : 2, 'FIFO' : 3}
cache_node = {'tag' : None, 'rp_crit' : None}

class Cache(object):
	def __init__(self, filename = None):
		self.block_size = 0
		self.cache_size = 0
		self.assoc = 0
		self.rp_policy = 0
		self.cache = []
		self.nread_accesses = 0
		self.nwrite_accesses = 0
		self.nread_misses = 0
		self.nwrite_misses = 0
		self.config_file = filename
		self.__read_config()
		self.__init_cache()

	def __read_config(self):
		try:
			with open(self.config_file, "rb") as config:
				for line in config:
					words = line.split() # separate words in the line
					if words[0] == 'blockSize':
						self.block_size = int(words[2], 0)
					elif words[0] == 'cacheSize':
						self.cache_size = int(words[2], 0)
					elif words[0] == 'assoc':
						self.assoc = int(words[2], 0)
					elif words[0] == 'replacementPolicy':
						self.rp_policy = replace_pol[words[2]];
					else:
						print '====== ERROR ====='
						print 'Unknown configuration parameter in the config file'
						print line
						print 'Exiting...'
						sys.exit()

			if self.cache_size and self.block_size and self.assoc and self.rp_policy:
				self.sets = (self.cache_size / self.block_size) / self.assoc
			else:
				print '====== ERROR ====='
				print 'Not all required parameters in the config file'
				print 'Exiting...'
				sys.exit()

		except IOError as error:
			print "Error opening file", error.filename
			print error.message
			sys.exit()


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

