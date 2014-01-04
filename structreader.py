# -*- coding: utf-8 -*-

import struct

class StructReader():
	'''
	This module simpliefies binary access to sockets. It will buffer socket input automatically.
	
	You define the format of your data with StructReader.add_struct. See struct.unpack for format definition.
	
	Examples:
	
		StructReader.add_struct("char", "c")
		StructReader.get_char() # will return a char
	
		StructReader.add_struct("byte", "b")
		StructReader.get_byte() # will return a byte
	
		StructReader.add_struct("myformat", "bhc")
		StructReader.get_myformat() # will return a tuple containing a byte, a short and a char
	
	'''
	
	prefix = "get_"
	
	def __init__(self, source):
		self.structs = {}
		self.source = source
		self.buffer = ""
	
	def add_struct(self, name, format):
		self.structs[name] = struct.Struct(format)
		
		if hasattr(self, self.prefix+name):
			delattr(self, self.prefix+name)
	
	def __getattr__(self, key):
		if key.startswith(self.prefix):
			name = key[len(self.prefix):]
			
			if name in self.structs:
				s = self.structs[name]
				
				def get():
					while len(self.buffer) < s.size:
						data = self.source.recv(4096)
						if data == "":
							raise EOFError
						self.buffer += data
					
					result = s.unpack_from(self.buffer)
					self.buffer = self.buffer[s.size:]
					
					if len(result) == 1:
						return result[0]
					return result
				
				setattr(self, self.prefix+name, get)
				return get
		
		return object.__getattribute__(self, key)
	

