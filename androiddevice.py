#!/usr/bin/env python
#
# tidevtools ti_android_device.py
# Copyright (c) 2011 by Bill Dawson
# Licensed under the terms of the Apache Public License
# Please see the LICENSE included with this distribution for details.
# http://github.com/billdawson/tidevtools

"""Get information about Android devices connected to your desktop and
run some adb commands on them.

>>> import androiddevice
>>> for device in androiddevice.get_connected_devices():
...     print device.serial_number
... 
HT05APL03677
02884149416070D7
emulator-5554
>>> 
"""

import re, sys
from subprocess import Popen, PIPE, call

class AndroidDevice(object):
	UNKNOWN = 0
	DEVICE = 1
	EMULATOR = 2
	prog_device = re.compile(r"^([^\s]+)\s+([^\s]+)$")
	def __init__(self, device_type=UNKNOWN, serial_number=None, parse_line=None):
		self.serial_number = serial_number
		self.device_type = device_type
		self._can_read_data_dir = None
		if parse_line is not None:
			m = AndroidDevice.prog_device.match(parse_line)
			if m is not None and len(m.groups()) == 2:
				self.serial_number = m.groups()[0]
				if self.serial_number.startswith("emulator"):
					self.device_type = AndroidDevice.EMULATOR
				else:
					self.device_type = AndroidDevice.DEVICE

	def is_emulator(self):
		return self.device_type == AndroidDevice.EMULATOR

	def is_device(self):
		return self.device_type == AndroidDevice.DEVICE

	def type_string(self):
		if self.device_type == AndroidDevice.UNKNOWN:
			return "unknown"
		elif self.device_type == AndroidDevice.EMULATOR:
			return "emulator"
		elif self.device_type == AndroidDevice.DEVICE:
			return "device"
		else:
			return ".device_type set to unknown value"

	def adb_arg_set(self):
		return ["adb", "-s", self.serial_number]

	def get_packages(self):
		args = self.adb_arg_set()
		if not self.can_read_data_dir():
			args.extend(("shell", "pm list packages"))
			output, outerr = Popen(args, stdout=PIPE, stderr=PIPE).communicate()
			if len(outerr) > 0:
				print >> sys.stderr, outerr
			if len(output) > 0:
				return [line.strip()[8:] for line in output.split("\n") if "package:" in line]
			else:
				return []
		else:
			# Parsing through contents of /data/data is faster than pm list packages
			args.extend(("shell", "ls /data/data"))
			output, outerr = Popen(args, stdout=PIPE, stderr=PIPE).communicate()
			if len(outerr) > 0:
				print >> sys.stderr, outerr
			if len(output) > 0:
				return [p.strip() for p in output.split("\n") if "." in p]
			else:
				return []

	def can_read_data_dir(self):
		if self._can_read_data_dir is not None:
			return self._can_read_data_dir
		args = self.adb_arg_set()
		args.extend(("shell", "ls /data/data || echo FAIL"))
		p = Popen(args, stdout=PIPE, stderr=PIPE)
		outdata, outerr = p.communicate()
		if len(outerr) > 0 or p.returncode != 0 or "FAIL" in outdata:
			self._can_read_data_dir = False
		else:
			self._can_read_data_dir = True
		return self._can_read_data_dir

	def has_package(self, package_name):
		return package_name in self.get_packages()

	def get_matching_packages(self, name_startswith):
		return [package.strip() for package in self.get_packages() if package.startswith(name_startswith)]

	def install(self, apk_path):
		args = self.adb_arg_set()
		args.extend(("install", "-r", apk_path))
		call(args)

	def uninstall(self, package_name):
		args = self.adb_arg_set()
		args.extend(("uninstall", package_name))
		call(args)
		self.shell_exec("rm -r /sdcard/%s" % package_name, silent=True)

	def shell_exec(self, shell_command, silent=False):
		args = self.adb_arg_set()
		args.extend(["shell", shell_command])
		if silent:
			return Popen(args, stdout=PIPE, stderr=PIPE)
		else:
			call(args)
			return (None, None)

	def __repr__(self):
		return self.serial_number

	@classmethod
	def is_device_line(cls, line):
		return cls.prog_device.match(line) is not None

def get_connected_devices():
	devices = []
	output, outerr= Popen(["adb", "devices"], stdout=PIPE, stderr=PIPE).communicate()
	if len(outerr) > 0:
		print >> sys.stderr, outerr
	if len(output) > 0:
		lines = output.split("\n")
		for line in lines:
			if AndroidDevice.is_device_line(line):
				devices.append(AndroidDevice(parse_line=line))
	return devices

if __name__ == "__main__":
	print get_connected_devices()
