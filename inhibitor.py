import dbus
import os
import subprocess

class DummyScreenSaver:
	def __init__(self):
		print("Cannot inhibit screensaver!")
	
	def inhibit(self):
		pass
	
	def uninhibit(self):
		pass
	
	def is_inhibited(self):
		return False
	

class GnomeScreenSaver:
	def __init__(self):
		try:
			bus = dbus.SessionBus()
			obj = bus.get_object("org.gnome.ScreenSaver", "/")
		except dbus.exceptions.DBusException:
			raise NotImplementedError
		
		self.screensaver = dbus.Interface(obj, "org.gnome.ScreenSaver")
		self.cookie = None
	
	def inhibit(self):
		if self.cookie != None:
			return False
		
		self.cookie = self.screensaver.Inhibit("GameDroid", "GameDroid is running")
		return True
	
	def uninhibit(self):
		if self.cookie == None:
			return False
		
		self.screensaver.UnInhibit(self.cookie)
		self.cookie = None
		return True
	
	def is_inhibited(self):
		return self.cookie != None
	

class XDGScreenSaver:
	def __init__(self):
		self.inhibited = False
		try:
			subprocess.call(['xdg-screensaver', 'status'], stdout=open(os.devnull, "w"))
			self.window_id = subprocess.Popen('xwininfo -root | grep xwininfo | cut -d" " -f4', stdout=subprocess.PIPE, shell=True).stdout.read().strip()
		except OSError:
			raise NotImplementedError
	
	def inhibit(self):
		if self.inhibited:
			return False
		
		subprocess.call(['xdg-screensaver', 'suspend', self.window_id])
		self.inhibited = True
		return True
	
	def uninhibit(self):
		if not self.inhibited:
			return False
		
		subprocess.call(['xdg-screensaver', 'resume', self.window_id])
		self.inhibited = False
		return True
	
	def is_inhibited(self):
		return self.inhibited
	

for ScreenSaver in (GnomeScreenSaver, XDGScreenSaver, DummyScreenSaver):
	try:
		screensaver = ScreenSaver()
	except NotImplementedError:
		continue
	else:
		break

def start():
	return screensaver.inhibit()

def stop():
	return screensaver.uninhibit()

def is_inhibited():
	return screensaver.is_inhibited()

