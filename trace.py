# !/usr/bin/env python

'''
Author: Jagadeesh Gaddipati
SID: 861196271
Email: jgadd001@ucr.edu

Notes:
Instruction Trace is a dictionary of the format
{'inst' : LD/ST, 'addr' : 0xFFFFFFFF} contained
in trace[] list of the Trace object
'''

import sys

class Trace(object):
	def __init__(self, filename = None):
		self.trace = []
		self.filename = filename
		self.__load_trace()

	def __load_trace(self):
		try:
			with open(self.filename, "rb") as trace:
				for line in trace:
					words = line.split() # separate words in the line
					if words[7] == 'L':
						temp_node = {'inst' : 'LD', 'addr' : int(words[9], 16)} # reading in hex
						self.trace.append(temp_node)
					elif words[7] == 'S':
						temp_node = {'inst' : 'ST', 'addr' : int(words[9], 16)} # reading in hex
						self.trace.append(temp_node)

				#for i in range(len(self.trace)):
				#	print self.trace[i]

		except IOError as error:
			print '====== ERROR ====='
			print "Error opening file", error.filename
			print error.message
			sys.exit()
