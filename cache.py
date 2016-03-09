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
import math
from random import randint

replace_pol = {'Random' : 1,
			   'LRU'    : 2,	# Least Recently Used
			   'FIFO'   : 3,	# First In First Out
			   'LFU'    : 4}	# Least Frequently Used

cache_node = {'tag'     : None,
			  'rp_crit' : 0,
			  'valid'   : 0}


class Cache(object):
	def __init__(self, filename = None):
		self.block_size = 0
		self.cache_size = 0
		self.assoc = 0
		self.rp_policy = 0
		self.sets = 0
		self.nread_accesses = 0
		self.nwrite_accesses = 0
		self.nread_misses = 0
		self.nwrite_misses = 0
		self.config_file = filename
		self.__cache = []
		self.__read_config()
		self.__init_cache()

	'''
	===========================================================================
	Local Functions
	===========================================================================
	'''

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
					temp_set.append(cache_node.copy())
				self.__cache.append(temp_set)

		else:
			print "Oops! This should not happen"
			sys.exit()


	def __do_cache_access(self, addr, inst):
		if inst == 'LD':
			self.nread_accesses += 1
		else:
			self.nwrite_accesses += 1

		if not self.__find_line(addr):
			#print "MISS"
			if inst == 'LD':
				self.nread_misses += 1
			else:
				self.nwrite_misses += 1

			self.__fill_line(addr)


	def __fill_line(self, addr):
		tag = self.__get_tag(addr)
		index = self.__get_index(addr)
		replace_req = True

		# find an empty line at 'index'th location set
		# there will be 'assoc' number of lines possible
		for line in range(self.assoc):
			if self.__cache[index][line]['tag'] == None:
				replace_req = False
				self.__cache[index][line]['tag'] = tag
				# newly added line, set replacement criteria accordingly
				self.__init_replace_crit(self.__cache[index], line)
				break

		# all positions are filled, replace a line accordingly
		if replace_req:
			self.__replace_line(tag, index)


	def __find_line(self, addr):
		tag = self.__get_tag(addr)
		index = self.__get_index(addr)

		# check the tags at 'index'th location set
		# there will be 'assoc' number of tags associated at that index
		for line in range(self.assoc):
			if self.__cache[index][line]['tag'] == tag:
				self.__update_replace_crit(self.__cache[index], line)
				return True
		return False


	def __replace_line(self, tag, index):
		cache_set = self.__cache[index]

		if self.rp_policy == 1:
			# Random
			random_line = randint(0, self.assoc - 1)
			cache_set[random_line]['tag'] = tag
			self.__init_replace_crit(cache_set, random_line)

		elif self.rp_policy == 2:
			# LRU -
			# gather ages of all lines
			lru_cnt = []
			for line in range(self.assoc):
				if cache_set[line]['tag']:
					lru_cnt.append(cache_set[line]['rp_crit'])

			# find the line with highest age and replace it
			lru_crit = max(lru_cnt)
			for line in range(self.assoc):
				if cache_set[line]['rp_crit'] == lru_crit:
					cache_set[line]['tag'] = tag
					# update replacement criteria since this is a new tag
					self.__init_replace_crit(cache_set, line)
					break

		elif self.rp_policy == 3:
			# FIFO -
			# decrement all fifo indices
			for i in range(self.assoc):
				if cache_set[i]['tag']:
					cache_set[i]['rp_crit'] -= 1

			# replace the tag with '0' fifo index since it entered the cache
			# before all the other tags present
			for i in range(self.assoc):
				if cache_set[i]['tag']:
					if cache_set[i]['rp_crit'] == 0:
						cache_set[i]['tag'] = tag
						# update replacement criteria since this is a new tag
						self.__init_replace_crit(cache_set, i)
						break

		elif self.rp_policy == 4:
			# LFU - Least Frequently Used
			# get the count of accesses of all the tags
			access_cnt = []
			for i in range(len(self.assoc)):
				if cache_set[i]['tag']:
					access_cnt.append(cache_set['rp_crit'])

			# replace a line that is least frequently accessed
			lfu_crit = min(access_cnt)
			for i in range(len(self.assoc)):
				if cache_set[i]['rp_crit'] == lfu_crit:
					cache_set[i]['tag'] = tag
					# update replacement criteria since this is a new tag
					self.__init_replace_crit(cache_set, i)
					break

		else:
			pass
		# TODO can add other policies


	def __init_replace_crit(self, cache_set, line):
		if self.rp_policy == 1:
			# Random - Nothing to do
			pass

		elif self.rp_policy == 2:
			# LRU - initialize age to 0, increment others' age
			for i in range(self.assoc):
				if i == line:
					cache_set[i]['rp_crit'] = 0
				else:
					if cache_set[i]['tag']:
						cache_set[i]['rp_crit'] += 1

		elif self.rp_policy == 3:
			# FIFO - set to the next fifo count
			# gather fifo counts of all tags
			fifo_cnt = []
			for i in range(self.assoc):
				if cache_set[i]['tag']:
					fifo_cnt.append(cache_set[i]['rp_crit'])

			# if this is the first to arrive, init to 1
			# otherwise set to the next fifo count
			if len(fifo_cnt):
				cache_set[line]['rp_crit'] = max(fifo_cnt) + 1
			else:
				cache_set[line]['rp_crit'] = 1

		elif self.rp_policy == 4:
			# LFU - Least Frequently Used
			# since this a new line, init to 0
			cache_set[line]['rp_crit'] = 0

		else:
			pass
		# TODO can add other policies


	def __update_replace_crit(self, cache_set, line):
		if self.rp_policy == 1:
			# Random - Nothing to do
			pass

		elif self.rp_policy == 2:
			# LRU - touch the block
			lru_age = 0
			for i in range(self.assoc):
				if i == line:
					lru_age = cache_set[i]['rp_crit']
					cache_set[i]['rp_crit'] = 0
					break

			# increment only those age which are less than that of the touched block
			for i in range(self.assoc):
				if i == line:
					continue
				else:
					if (cache_set[i]['tag']) && (cache_set[i]['rp_crit'] < lru_age):
						cache_set[i]['rp_crit'] += 1

		elif self.rp_policy == 3:
			# FIFO - Nothing to do
			pass

		elif self.rp_policy == 4:
			# LFU - Least Frequently Used
			# line is accessed, increment criteria
			cache_set[line]['rp_crit'] += 1

		else:
			pass
		# TODO add other policies


	def __get_tag(self, addr):
		tag = addr

		# tag_bits = 32 - log2(n_sets) - log2(block_size)
		# remove the bits from the address which do not form the tag

		not_tag_bits = int(math.log(self.sets, 2) + math.log(self.block_size, 2))
		for n_bits in range(not_tag_bits):
			tag = tag >> 1
		return tag


	def __get_index(self, addr):
		# idx_bits = log2(n_sets)
		idx_offset_bits = int(math.log(self.sets, 2) + math.log(self.block_size, 2))

		# generate mask to remove tag bits
		mask = 1
		for n_bits in range(idx_offset_bits - 1):
			mask = (mask << 1) | 0x01
		idx = addr & mask

		# remove the block offset bits
		for n_bits in range(int(math.log(self.block_size, 2))):
			idx = idx >> 1

		return idx


	def __printhex(self, num):
		print '0x' + format(num, '08X')


	'''
	===========================================================================
	Public Functions
	===========================================================================
	'''


	def run(self, inst_trace):
		# iterate over the instructions one by one
		for tr in iter(inst_trace):
			if tr['inst'] == 'LD' or tr['inst'] == 'ST':
				self.__do_cache_access(tr['addr'], tr['inst'])
			'''
			print
			for i in range(len(self.__cache)):
			#	print (self.__cache[i])
				for j in range(self.assoc):
					if self.__cache[i][j]['tag'] != None:
						print '0x' + format(self.__cache[i][j]['tag'], '08X'),
					else:
						print None,
				print
			'''


	def print_stats(self):
		print
		print "============ Stats ========================="
		print 'Number of Read Accesses  :', self.nread_accesses
		print 'Number of Write Accesses :', self.nwrite_accesses

		n_accesses = self.nwrite_accesses + self.nread_accesses
		print 'Total Cache Accesses     :', n_accesses

		print 'Number of Read Misses    :', self.nread_misses
		print 'Number of Write Misses   :', self.nwrite_misses

		n_misses = self.nwrite_misses + self.nread_misses
		print 'Total Cache Misses       :', n_misses

		miss_rate = float(n_misses) / n_accesses
		print 'Miss Rate                :', miss_rate

		amat = 1 + (miss_rate * 100)
		print 'Avg Memory Access Time   :', amat

		print
