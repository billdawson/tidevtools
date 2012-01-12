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
import os, sys, platform, re
from os import environ as env
from xml.dom.minidom import parse, Node

def is_linux():
	return platform.system() == 'Linux'

def is_windows():
	p = platform.system()
	return p == 'Windows' or 'CYGWIN' in p

def is_osx():
	return platform.system() == 'Darwin'

def find_ti_sdk(version=None):
	"""Returns a tuple (path, version).  Path goes all the way down to the version"""
	tisdk_path = ''
	sdkver = ''
	if is_osx():
		tisdk_path = os.path.join('/', 'Library', 'Application Support', 'Titanium', 'mobilesdk', 'osx')
		if not os.path.exists(tisdk_path):
			tisdk_path = os.path.expanduser("~%s" % tisdk_path)
	elif is_linux():
		tisdk_path = os.path.expanduser(os.path.join('~', '.titanium', 'mobilesdk', 'linux'))
	else:
		# win7
		tisdk_path = os.path.join('C:\\', 'ProgramData', 'Titanium', 'mobilesdk', 'win32')
		if not os.path.exists(tisdk_path):
			# try xp
			tisdk_path = os.path.join('C:\\', 'Documents and Settings', 'All Users', 'Application Data', 'Titanium', 'mobilesdk', 'win32')

	# let environment override
	if 'TI_DEV_SDK' in os.environ:
		ti_dev_sdk = os.environ['TI_DEV_SDK']
		if os.path.exists(ti_dev_sdk):
			version = os.path.basename(ti_dev_sdk)
			return (ti_dev_sdk, version)
		else:
			print 'Warning: TI_DEV_SDK is set, but the path doesn\'t exist'

	if not version is None:
		tisdk_path = os.path.join(tisdk_path, version)
		sdkver = version
	else:
		sdkver = ''
		# hunt for the latest sdk simply by mod date of version folders
		subs = os.listdir(tisdk_path)
		if not subs:
			print "I couldn't find any subdirectories of %s." % tisdk_pat
			sys.exit(1)
		subdirs = [s for s in subs if os.path.isdir(os.path.join(tisdk_path, s))]
		subdirs = [s for s in subdirs if os.path.exists(os.path.join(tisdk_path, s, 'version.txt'))]
		maxtime = None
		for onedir in subdirs:
			thistime = os.path.getmtime(os.path.join(tisdk_path, onedir, "version.txt"))
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
		tidev_db = os.path.join(env['USERPROFILE'], 'AppData', 'Roaming', 'Titanium')
	elif is_linux():
		tidev_db = os.path.expanduser('~/.titanium')
	else:
		tidev_db = os.path.join(os.path.expanduser('~/Library'), 'Application Support', 'Titanium')

	tidev_db = os.path.join(tidev_db, 'appdata', 'com.appcelerator.titanium.developer', 'app_com.appcelerator.titanium.developer_0', '0000000000000001.db')
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
			if os.path.exists(onecheck):
				android_sdk = onecheck
				break

	if len(android_sdk) == 0:
		if "ANDROID_SDK" in env:
			if os.path.exists(env['ANDROID_SDK']):
				android_sdk = env['ANDROID_SDK']
	return android_sdk

def appid_to_path(appid):
	return os.sep.join(appid.split('.'))

def get_node_text(nodelist):
	rc = []
	for node in nodelist:
		if node.nodeType == node.TEXT_NODE:
			rc.append(node.data)
	return ''.join(rc)

def get_app_info(project_root):
	tiapp_xml = os.path.join(os.path.join(project_root, 'tiapp.xml'))
	if not os.path.exists(tiapp_xml):
		raise Exception('%s does not exist' % tiapp_xml)
	tiapp = parse(tiapp_xml)
	root = tiapp.documentElement
	app_info = {}
	for element in root.childNodes:
		if element.nodeType != Node.ELEMENT_NODE: continue
		app_info[element.nodeName] = get_node_text(element.childNodes);
	return app_info

def get_appid(project_root):
	return get_app_info(project_root)['id']

def ti_module_exists(module):
	tisdk = find_ti_sdk()[0]
	return os.path.exists(os.path.join(tisdk, 'android', 'modules', '%s.jar' % module))

def is_mobile_repo(repo_dir):
	return os.path.exists(os.path.join(repo_dir, "SConstruct")) \
		and os.path.exists(os.path.join(repo_dir, "build", "titanium_version.py"))

def find_mobile_repo(max_depth=5):
	repo_dir = os.path.abspath(os.getcwd())
	depth = 1
	while depth < max_depth:
		if is_mobile_repo(repo_dir):
			return repo_dir
		if repo_dir == os.path.dirname(repo_dir):
			return None
		repo_dir = os.path.dirname(repo_dir)
	return None
