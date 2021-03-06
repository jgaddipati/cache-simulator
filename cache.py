# !/usr/bin/env python

'''
Author: Jagadeesh Gaddipati
Email: jgadd001@ucr.edu

Notes:
Cache is arranged as a list of cache sets. Each cache set is a list of cache_node
dictionaries. The number of cache sets depend on associativity of the cache.

rp_crit values:
LRU  - age of cache block, when block is accessed(touched), initialize age to 0 and increment others' ages
FIFO - entry index of the cache block (first entered=0, second entered=1, ...)
LFU  - number of times the cache block is accessed
'''

import sys
import math
from random import randint

write_pol = {'WRITE_BACK'    : 1,
             'WRITE_THROUGH' : 2}

replace_pol = {'RANDOM' : 1,
	       'LRU'    : 2,	# Least Recently Used
	       'FIFO'   : 3,	# First In First Out
	       'LFU'    : 4}	# Least Frequently Used

cache_node = {'tag'     : None,	# tag
	      'rp_crit' : 0,	# replacement criteria, see notes above
	      'valid'   : 0,	# valid bit (used for cache coherence, not implemented yet)
	      'dirty'   : 0}	# dirty bit for write policy (Write-back or Write-through)


class Cache(object):
	def __init__(self, filename = None):
		self.block_size = 0
		self.cache_size = 0
		self.assoc = 0
		self.rp_policy = 0
		self.wr_policy = 0
		self.sets = 0
		self.nread_accesses = 0
		self.nwrite_accesses = 0
		self.nread_misses = 0
		self.nwrite_misses = 0
		self.evictions = 0
		self.writes_to_wr_buff = 0
		self.cycles = 0
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
					# handle empty lines in the config file
					if line.strip() == '':
						continue

					words = line.split() # separate words in the line
					if words[0] == 'blockSize':
						self.block_size = int(words[2], 0)
					elif words[0] == 'cacheSize':
						self.cache_size = int(words[2], 0)
					elif words[0] == 'assoc':
						self.assoc = int(words[2], 0)
					elif words[0] == 'replacementPolicy':
						self.rp_policy = replace_pol[words[2]];
					elif words[0] == 'writePolicy':
						self.wr_policy = write_pol[words[2]]
					else:
						print '====== ERROR ====='
						print 'Unknown configuration parameter in the config file'
						print line
						print 'Exiting...'
						sys.exit()

			if self.cache_size and self.block_size and self.assoc and self.rp_policy and self.wr_policy:
				self.sets = (self.cache_size / self.block_size) / self.assoc
			else:
				print '====== ERROR ====='
				print 'Not all required parameters in the config file'
				print 'Required: blockSize, cacheSize, assoc, replacementPolicy, writePolicy'
				print 'Exiting...'
				sys.exit()

		except IOError as error:
			print "Error opening", error.filename, "file"
			print error.message
			print "Please ensure that 'config' file is present"
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

		if not self.__find_line(addr, inst):
			if inst == 'LD':
				self.nread_misses += 1
			else:
				self.nwrite_misses += 1

			self.__fill_line(addr, inst)


	def __find_line(self, addr, inst):
		tag = self.__get_tag(addr)
		index = self.__get_index(addr)

		# check the tags at 'index'th location set
		cache_set = self.__cache[index]

		for line in range(self.assoc):
			if cache_set[line]['valid'] and (cache_set[line]['tag'] == tag):

				# takes 1 cycle to send data to processor on hit
				self.cycles += 1
				self.__update_replace_crit(cache_set, line)
				if inst == 'ST':
					self.__act_write_policy(cache_set[line])
				return True
		return False


	def __fill_line(self, addr, inst):
		tag = self.__get_tag(addr)
		index = self.__get_index(addr)
		replace_req = True

		# filling a cache line with memory from
		# lower level cache takes 100 cycles
		self.cycles += 100

		# find an empty line at 'index'th location set
		cache_set = self.__cache[index]

		for line in range(self.assoc):
			if cache_set[line]['tag'] == None:
				replace_req = False
				cache_set[line]['tag'] = tag
				cache_set[line]['valid'] = 1
				if inst == 'ST':
					self.__act_write_policy(cache_set[line])

				# newly added line, init replacement criteria accordingly
				self.__init_replace_crit(cache_set, line)
				break

		# all positions are filled, replace a line according to policy
		if replace_req:
			self.__replace_line(tag, index, inst)

		# takes additional 1 cycle to send filled data to processor on miss
		self.cycles += 1


	def __replace_line(self, tag, index, inst):

		self.evictions += 1
		cache_set = self.__cache[index]

		if self.rp_policy == 1:
			# Random
			random_line = randint(0, self.assoc - 1)

			# before evicting a block, write to write buffer if it is dirty
			if self.wr_policy == 1: # WRITE_BACK
				if cache_set[random_line]['dirty']:
					self.writes_to_wr_buff += 1

			# now fill with new block
			cache_set[random_line]['tag'] = tag
			cache_set[random_line]['valid'] = 1
			if inst == 'ST':
				self.__act_write_policy(cache_set[random_line])

			# init replacement criteria since this is a new tag
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

					# before evicting a block, write to write buffer if it is dirty
					if self.wr_policy == 1: # WRITE_BACK
						if cache_set[line]['dirty']:
							self.writes_to_wr_buff += 1

					# now fill with new block
					cache_set[line]['tag'] = tag
					cache_set[line]['valid'] = 1
					if inst == 'ST':
						self.__act_write_policy(cache_set[line])

					# init replacement criteria since this is a new tag
					self.__init_replace_crit(cache_set, line)
					break

		elif self.rp_policy == 3:
			# FIFO -
			# decrement all fifo indices
			for line in range(self.assoc):
				if cache_set[line]['tag']:
					cache_set[line]['rp_crit'] -= 1

			# replace the tag with '0' fifo index since it entered the cache
			# before all the other tags present
			for line in range(self.assoc):
				if cache_set[line]['tag']:
					if cache_set[line]['rp_crit'] == 0:

						# before evicting a block, write to write buffer if it is dirty
						if self.wr_policy == 1: # WRITE_BACK
							if cache_set[line]['dirty']:
								self.writes_to_wr_buff += 1

						# now fill with new block
						cache_set[line]['tag'] = tag
						cache_set[line]['valid'] = 1
						if inst == 'ST':
							self.__act_write_policy(cache_set[line])

						# init replacement criteria since this is a new tag
						self.__init_replace_crit(cache_set, line)
						break

		elif self.rp_policy == 4:
			# LFU -
			# get the count of accesses of all the tags
			access_cnt = []
			for line in range(self.assoc):
				if cache_set[line]['tag']:
					access_cnt.append(cache_set[line]['rp_crit'])

			# replace a line that is least frequently accessed
			lfu_crit = min(access_cnt)
			for line in range(self.assoc):
				if cache_set[line]['rp_crit'] == lfu_crit:

					# before evicting a block, write to write buffer if it is dirty
					if self.wr_policy == 1: # WRITE_BACK
						if cache_set[line]['dirty']:
							self.writes_to_wr_buff += 1

					# now fill with new block
					cache_set[line]['tag'] = tag
					cache_set[line]['valid'] = 1
					if inst == 'ST':
						self.__act_write_policy(cache_set[line])

					# init replacement criteria since this is a new tag
					self.__init_replace_crit(cache_set, line)
					break

		# TODO add other policies here
		else:
			pass


	def __init_replace_crit(self, cache_set, line):

		if self.rp_policy == 1:
			# Random - Nothing to do
			pass

		elif self.rp_policy == 2:
			# LRU - initialize age to 0, increment others' age
			for iter_line in range(self.assoc):
				if iter_line == line:
					cache_set[iter_line]['rp_crit'] = 0
				else:
					if cache_set[iter_line]['tag']:
						cache_set[iter_line]['rp_crit'] += 1

		elif self.rp_policy == 3:
			# FIFO - set to the next fifo count
			# gather fifo counts of all tags
			fifo_cnt = []
			for iter_line in range(self.assoc):
				if cache_set[iter_line]['tag']:
					fifo_cnt.append(cache_set[iter_line]['rp_crit'])

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

		# TODO add other policies here
		else:
			pass


	def __update_replace_crit(self, cache_set, line):
		if self.rp_policy == 1:
			# Random - Nothing to do
			pass

		elif self.rp_policy == 2:
			# LRU - touch the block
			replaced_age = 0
			for iter_line in range(self.assoc):
				if iter_line == line:
					replaced_age = cache_set[iter_line]['rp_crit']
					cache_set[iter_line]['rp_crit'] = 0
					break

			# increment only those age which are less than that of the touched block
			# in this way, the counters wont get beyond the saturation value
			for iter_line in range(self.assoc):
				if iter_line != line:
					if cache_set[iter_line]['tag'] and (cache_set[iter_line]['rp_crit'] < replaced_age):
						cache_set[iter_line]['rp_crit'] += 1

		elif self.rp_policy == 3:
			# FIFO - Nothing to do
			pass

		elif self.rp_policy == 4:
			# LFU - Least Frequently Used
			# line is accessed, increment criteria
			cache_set[line]['rp_crit'] += 1

		# TODO add other policies here
		else:
			pass


	def __act_write_policy(self, cache_line):
		if self.wr_policy == 1:
			cache_line['dirty'] = 1 # WRITE_BACK, set dirty bit
		else:
			self.writes_to_wr_buff += 1 # WRITE_THROUGH, write to write_buffer also


	def __get_tag(self, addr):
		tag = addr

		# tag_bits = 32 - log2(n_sets) - log2(block_size)
		# remove the bits from the address which do not form the tag

		not_tag_bits = int(math.log(self.sets, 2) + math.log(self.block_size, 2))
		for n_bits in range(not_tag_bits):
			tag = tag >> 1
		return tag


	def __get_index(self, addr):
		# idx_bits = log2(n_sets), offset_bits = log2(block_size)
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

	"""
	def run(self, inst_trace):
		# iterate over the instructions one by one
		for tr in iter(inst_trace):
			if tr['inst'] == 'LD' or tr['inst'] == 'ST':
				self.__do_cache_access(tr['addr'], tr['inst'])
	"""


	def run(self, inst_node):
		self.__do_cache_access(inst_node['addr'], inst_node['inst'])


	def print_stats(self):

		n_accesses = self.nwrite_accesses + self.nread_accesses
		n_misses = self.nwrite_misses + self.nread_misses
		miss_rate = float(n_misses) / n_accesses
		amat = float(self.cycles) / n_accesses

		print
		print "============ Stats ========================="
		print 'Total Memory Accesses            :', n_accesses
		print 'Number of Read Accesses          :', self.nread_accesses
		print 'Number of Write Accesses         :', self.nwrite_accesses
		print

		print 'Total Cache Hits                 :', n_accesses - n_misses
		print 'Number of Read Hits              :', self.nread_accesses - self.nread_misses
		print 'Number of Write Hits             :', self.nwrite_accesses - self.nwrite_misses
		print

		print 'Total Cache Misses               :', n_misses
		print 'Number of Read Misses            :', self.nread_misses
		print 'Number of Write Misses           :', self.nwrite_misses
		print

		print 'Cache Block Evictions            :', self.evictions
		print 'Number of writes to WriteBuffer  :', self.writes_to_wr_buff
		print

		print 'Miss Rate                        : {:.2f} %'.format(miss_rate * 100)
		print 'Avg Memory Access Time(cycles)   : {:.2f}'.format(amat)
		print


	def print_config(self):
		print
		print "=========== Configuration =================="
		print 'Cache size           :', self.cache_size
		print 'Block size           :', self.block_size
		print 'Associativity        :', self.assoc
		print 'Replacement criteria :', [key for key, value in replace_pol.iteritems() if value == self.rp_policy]
		print 'Write Policy         :', [key for key, value in write_pol.iteritems() if value == self.wr_policy]
		print
