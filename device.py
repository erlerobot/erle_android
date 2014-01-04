# -*- coding: utf-8 -*-

from __future__ import print_function

import bluetooth
import socket
import sys
import threading
import uinput

import structreader

class Device(threading.Thread):
	def __init__(self, server, socket):
		threading.Thread.__init__(self)
		
		self.daemon = True
		self.socket = socket
		self.server = server
		
		self.peer = self.socket.getpeername() # when socket gets disconnected
		print("Device [%s]:%d has connected   " % self.peer, end=' ')
		sys.stdout.flush()
		
		self.reader = structreader.StructReader(self.socket)
		self.reader.add_struct("char", "c")
		self.reader.add_struct("byte", "b")
		self.reader.add_struct("short", "!h")
		self.reader.add_struct("event", "!hh")
		
		self.start()
	
	def handshake(self):
		events = []
		
		name = ""
		while True:
			char = self.reader.get_char()
			
			if char == "\0":
				break
			
			name += char
		
		self.name = name
		
		while True:
			typeno = self.reader.get_byte()
			if typeno == 0:
				break
			
			key = self.reader.get_short()
			
			event = [typeno, key]
			
			if typeno > 2: # ABS controls
				event.append(-32768) # absmax
				event.append(32767)  # absmin
				event.append(0)      # absfuzzin
				event.append(0)      # absflat
			
			events.append(event)
		
		print("- creating gamepad '%s'" % self.name)
		sys.stdout.flush()
		self.device = uinput.Device(events, name=self.name)
		
		self.server.on_device_connected()
	
	def run(self):
		try:
			self.handshake()
			
			while True:
				event_type = self.reader.get_byte()
				
				if event_type == 0:
					self.device.syn()
					continue
				
				event_key, value = self.reader.get_event()
				
				self.device.emit((event_type, event_key), value)
		except (bluetooth.BluetoothError, EOFError):
			try:
				self.socket.shutdown(socket.SHUT_RDWR)
			except Exception as ex:
				pass
			try:
				self.socket.close()
			except Exception as ex:
				pass
		except Exception as ex:
			import traceback
			traceback.print_exception(*sys.exc_info())
			sys.stdout.flush()
		finally:
			print("Device [%s]:%d has disconnected - removing gamepad '%s'" % (self.peer + (self.name, )))
			sys.stdout.flush()
			self.server.on_device_disconnected()
	

