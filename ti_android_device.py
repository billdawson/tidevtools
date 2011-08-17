#!/usr/bin/env python
#
# tidevtools ti_android_device.py
# Copyright (c) 2011 by Bill Dawson
# Licensed under the terms of the Apache Public License
# Please see the LICENSE included with this distribution for details.
# http://github.com/billdawson/tidevtools

"""With no command-line options, this script will evaluate the current directory
to see if it contains a Titanium project (i.e., has a tiapp.xml), then
present you with options to install/uninstall the project to/from any 
connected Android devices.

If, instead, you use the -u option, you will have the opportunity
to uninstall (-u) from your connected devices any packages whose names begin 
with the value you provide for -u. "-u com.appcelerator" will show you
any packages whose names begin with "com.appcelerator" and give you the
opportunity to remove them from your connected device(s)."""

import os, sys, re, optparse
from time import sleep
from subprocess import Popen, PIPE, call

this_script_file = os.path.abspath(__file__)
this_script_dir = os.path.dirname(this_script_file)
this_script_realdir = os.path.dirname(os.path.realpath(this_script_file))
cur_dir = os.path.abspath(os.getcwd())

sys.path.append(this_script_realdir)
from androiddevice import get_connected_devices

def restart_adb_server():
	call(["adb", "kill-server"])
	print "Sleeping 5 seconds..."
	sleep(5)
	call(["adb", "start-server"])

def get_project_package():
	package = None
	manifest = os.path.join(cur_dir, "build", "android", "AndroidManifest.xml")
	if os.path.exists(manifest):
		matches = re.findall(r'package="([^"]+)"', open(manifest, "r").read())
		if matches is not None and len(matches) > 0:
			package = matches[0]
	if package is None:
		tiapp = os.path.join(cur_dir, "tiapp.xml")
		if os.path.exists(tiapp):
			matches = re.findall(r'<id>([^<]+)</id>', open(tiapp, "r").read())
			if matches is not None and len(matches) > 0:
				package = matches[0]
	return package

# blank lines
def bl(num):
	for i in range(num):
		print ""

def repeat(s, num):
	result = ""
	for i in range(num):
		result += s
	return result

# blank spaces
def b(num):
	return repeat(" ", num)

def print_header(devices):
	bl(2)
	headers = (
			"Connected Devices: %s" % devices,
			"If this looks incorrect, enter 'r' to restart adb server."
			)
	print repeat("=", max([len(header) for header in headers]))
	print "\n".join(headers)
	bl(1)

def print_common_commands():
	print "OTHER"
	print repeat("-", len("other"))
	print "(r)\tRestart adb server. (Does kill-server, waits 5 secs, then start-server.)"
	print "(q)\tQuit this script."
	bl(1)

def choice_handler(options):
	raw = raw_input("Enter an option (or comma-sep options): ")
	choices = [choice.strip().lower() for choice in raw.split(",")]
	for choice in choices:
		if choice == "q":
			sys.exit(0)
		elif choice == "r":
			restart_adb_server()
		elif choice.isdigit() and int(choice) < len(options):
			fx = options[int(choice)]["function"]
			fx(options[int(choice)]["arg"])
			# Special case: if the function being executed is uninstall, also
			# remove the folder that Titanium apps put directly into the
			# sdcard root, e.g., /sdcard/com.appcelerator.titanium.
			if "uninstall" in str(fx):
				fx.__self__.shell_exec("rm -r /sdcard/%s" % options[int(choice)]["arg"], silent=True)
		else:
			print >> sys.stderr, "Ignoring invalid choice '%s'" % choice
	raw_input("Press <Enter> to continue...")

def do_immediate_uninstall():
	devices = get_connected_devices()
	print "Checking devices: %s" % devices
	package = get_project_package()
	did_one = False
	for d in devices:
		if d.has_package(package):
			print "Uninstalling %s from %s" % (package, d.serial_number)
			d.uninstall(package)
			did_one = True
	if not did_one:
		print "No attached devices contained %s" % package


def show_project_options():
	devices = get_connected_devices()
	print_header(devices)
	package = get_project_package()
	apk_path = os.path.join(cur_dir, "build", "android", "bin", "app.apk")
	options = []
	counter = 0
	for d in devices:
		print d.serial_number
		print repeat("-", len(d.serial_number))
		if d.has_package(package):
			options.append({
				"function": d.uninstall,
				"arg": package
				})
			print "(%s)\tUninstall %s from %s" % (counter, package, d.serial_number)
			counter += 1
		if os.path.exists(apk_path):
			options.append({
				"function": d.install,
				"arg": apk_path
				})
			print "(%s)\tInstall %s to %s" % (counter, os.path.relpath(apk_path), d.serial_number)
			counter += 1
		bl(1)
	print_common_commands()
	choice_handler(options)

def show_multi_uninstaller(package_filter):
	devices = get_connected_devices()
	print_header(devices)
	options = []
	found = False
	counter = 0
	for device in devices:
		packages = device.get_matching_packages(package_filter)
		if len(packages) == 0:
			continue
		found = True
		print device.serial_number
		print repeat("-", len(device.serial_number))
		for package in packages:
			print "(%s) Uninstall %s from %s." % (counter, package, device.serial_number)
			options.append({
				"function": device.uninstall,
				"arg": package
				})
			counter += 1
		bl(1)
	if not found:
		print "No packages found that start with '%s'." % package_filter
		bl(1)
	print_common_commands()
	choice_handler(options)

if __name__ == "__main__":
	parser = optparse.OptionParser(description=__doc__)
	parser.add_option("-u", "--uninstall",
			dest="package_filter",
			help="Show packages whose names begin with given value and give opportunity to uninstall them.")
	parser.add_option("-i", "--immediate",
			dest="immediate",
			action="store_true",
			default=False,
			help="Immediately uninstall app in your current directory from all connected devices that have it.")
	options, args = parser.parse_args()

	if not options.package_filter and not os.path.exists(os.path.join(cur_dir, "tiapp.xml")):
		print >> sys.stderr, "No tiapp.xml file found. Need to be in a titanium project folder unless you use the -u option."
		sys.exit(1)
	elif not options.package_filter and not options.immediate:
		while True:
			show_project_options()
	elif options.immediate:
		do_immediate_uninstall()
	else:
		while True:
			show_multi_uninstaller(options.package_filter)

