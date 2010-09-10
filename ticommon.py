#!/usr/bin/env python
"""
 * tidevtools 'ticommon' - Common stuff for the other tidevtools tools
 *
 * Copyright (c) 2010 by Bill Dawson
 * Licensed under the terms of the Apache Public License
 * Please see the LICENSE included with this distribution for details.
 * http://github.com/billdawson/tidevtools
 *
"""
import os, sys, platform
from os import environ as env

def is_windows():
	p = platform.system()
	return ('indows' in p or 'CYGWIN' in p)

def find_ti_sdk():
	"""Returns a tuple (path, version).  Path goes all the way down to the version"""
	isWindows = is_windows()
	tisdk_path = ''
	sdkver = ''
	if not isWindows:
		tisdk_path = os.path.join('/', 'Library', 'Application Support', 'Titanium', 'mobilesdk', 'osx')
	else:
		# win7
		tisdk_path = os.path.join('C:\\', 'ProgramData', 'Titanium', 'mobilesdk', 'win32')
		if not os.path.exists(tisdk_path):
			# try xp
			tisdk_path = os.path.join('C:\\', 'Documents and Settings', 'All Users', 'Application Data', 'Titanium', 'mobilesdk', 'win32')

	if os.path.exists(tisdk_path):
		sdkver = ''
		# hunt for the latest sdk simply by mod date of version folders
		subs = os.listdir(tisdk_path)
		if not subs:
			print "I couldn't find any subdirectories of %s." % tisdk_pat
			sys.exit(1)
		subdirs = [s for s in subs if os.path.isdir(os.path.join(tisdk_path, s))]
		subdirs = [s for s in subdirs if os.path.exists(os.path.join(tisdk_path, s, 'README'))]
		maxtime = None
		for onedir in subdirs:
			thistime = os.path.getmtime(os.path.join(tisdk_path, onedir))
			if maxtime is None:
				sdkver = onedir
				maxtime = thistime
			else:
				if thistime > maxtime:
					sdkver = onedir
					maxtime = thistime

		tisdk_path = os.path.join(tisdk_path, sdkver)
	return (tisdk_path, sdkver)

def find_ti_dev_db():
	tidev_db = ''
	# only works for win7 at the moment
	if is_windows():
		tidev_db = os.path.join(env['USERPROFILE'], 'AppData', 'Roaming')
	else:
		tidev_db = os.path.join(os.path.expanduser('~/Library'), 'Application Support')

	tidev_db = os.path.join(tidev_db, 'Titanium', 'appdata', 'com.appcelerator.titanium.developer', 'app_com.appcelerator.titanium.developer_0', '0000000000000001.db')
	if not os.path.exists(tidev_db):
		tidev_db = ''
	return tidev_db

def find_android_sdk():
	android_sdk_check = []
	android_sdk = ''
	
	if not is_windows():
		android_sdk_check = ['/opt/android-sdk-mac_86', '/opt/android-sdk', 
				os.path.expanduser('~/android-sdk-mac_86'),
				os.path.expanduser('~/android-sdk')]
		for onecheck in android_sdk_check:
			if os.path.exists(onecheck):
				android_sdk = onecheck
				break
	else:
		android_sdk_check = ['C:\\android-sdk-win_32', 'C:\\android-sdk']
		for onecheck in android_sdk_check:
			if os.path.exist(onecheck):
				android_sdk = onecheck
				break

	if len(android_sdk) == 0:
		if "ANDROID_SDK" in env:
			if os.path.exists(env['ANDROID_SDK']):
				android_sdk = env['ANDROID_SDK']
	return android_sdk

