#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import bluetooth
import select
import socket
import sys
import time
import threading

import device
import inhibitor

# TODO add some sort of GUI

class BluetoothServer():
	def __init__(self, server):
		self.server = server
		
		self.uuid = "00001101-0000-1000-8000-00805F9B34FB"
		self.sdpname = "GameDroid"
		self.port = 10
		
		self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		
		self.socket.bind(("", self.port))
		self.socket.listen(1)
		
		bluetooth.advertise_service(
			self.socket,
			self.sdpname,
			self.uuid,
			service_classes=[bluetooth.SERIAL_PORT_CLASS],
			profiles=[bluetooth.SERIAL_PORT_PROFILE]
		)
		
		print("Listening on [%s]:%d" % self.socket.getsockname())
	
	def on_read(self):
		client, address = self.socket.accept()
		device.Device(self.server, client)
	
	def get_fd(self):
		return self.socket.fileno()
	

class NetworkServer():
	def __init__(self, server):
		self.server = server
		
		self.port = 56365
		
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		
		self.socket.bind(("", self.port))
		self.socket.listen(1)
		
		print("Listening on [%s]:%d" % self.socket.getsockname())
	
	def on_read(self):
		client, address = self.socket.accept()
		device.Device(self.server, client)
	
	def get_fd(self):
		return self.socket.fileno()
	

class GameDroidServer:
	def __init__(self):
		self.lock = threading.Lock()
		self.devices = 0
		
		self.descriptors = {}
		self.poll = select.poll()
		
		try:
			self.server_bt = BluetoothServer(self)
		except bluetooth.btcommon.BluetoothError:
			pass
		else:
			self.add_server(self.server_bt)
		
		self.server_nw = NetworkServer(self)
		self.add_server(self.server_nw)
	
	def add_server(self, server):
		fd = server.get_fd()
		self.descriptors[fd] = server
		self.poll.register(fd, select.POLLIN)
	
	def on_device_connected(self):
		with self.lock as lock:
			self.devices += 1
			if self.devices == 1:
				print("Screensaver locked")
				inhibitor.start()
	
	def on_device_disconnected(self):
		with self.lock as lock:
			self.devices -= 1
			if self.devices == 0:
				print("Screensaver released")
				inhibitor.stop()
	
	def run(self): 
		while True:
			try:
				for fd, state in self.poll.poll():
					self.descriptors[fd].on_read()
			except KeyboardInterrupt:
				with self.lock as lock:
					devices = self.devices
				
				if devices == 0:
					break
				
				if devices == 1:
					print("\rOne gamepad is still connected.")
				else:
					print("\r%d gamepads are still connected." % devices)
				print("If you really want to interrupt, press Ctrl+C again.", end=' ')
				sys.stdout.flush()
				
				try:
					for i in range(5):
						time.sleep(1)
					print()
					continue
				except KeyboardInterrupt:
					break
		
		print() # clear line after ^C
	

def main():
	try:
		server = GameDroidServer()
		server.run()
	finally:
		if inhibitor.is_inhibited():
			inhibitor.stop()

if __name__ == "__main__":
	main()
	

