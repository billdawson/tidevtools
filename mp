#!/usr/bin/env python
"""
 * tidevtools
 * Copyright (c) 2010 by Bill Dawson
 * Licensed under the terms of the Apache Public License
 * Please see the LICENSE included with this distribution for details.
 * http://github.com/billdawson/tidevtools
 *
 * So just pass it a project name, it'll do the rest.  But first change the variables 
 * ("constants") below in the "CUSTOMIZE HERE" section. 
"""
print "tidevtools 'mp'"

import sys, os, uuid, re, sqlite3, time, datetime
from os import environ as env

######### CUSTOMIZE HERE ########################
PROJECT_ID_PREFIX = 'com.billdawson.'
PROJECT_FOLDER = '/Users/bill/projects/ti'
PUBLISHER = 'bill'
PUBLISHER_URL = 'billdawson.com'
DISABLE_ANALYTICS = True
ENABLE_ANDROID_DEBUG = True
#################################################
ANDROID_DEBUG = '<property type="bool" name="ti.android.debug">true</property>'

if len(sys.argv) < 2:
	print "Usage: %s <name>" % os.path.basename(sys.argv[0])
	sys.exit(1)

project_name = sys.argv[1]

isWindows = 'USERPROFILE' in env

# Find the Titanium Developer Sqlite database
tidev_db = ''
# only works for win7 at the moment
if isWindows:
	tidev_db = os.path.join(env['USERPROFILE'], 'AppData', 'Roaming')
else:
	tidev_db = os.path.join(os.path.expanduser('~/Library'), 'Application Support')

tidev_db = os.path.join(tidev_db, 'Titanium', 'appdata', 'com.appcelerator.titanium.developer', 'app_com.appcelerator.titanium.developer_0', '0000000000000001.db')

if not os.path.exists(tidev_db):
	print "I couldn't find your Titanium Developer sqlite db.  I looked in %s." % tidev_db
	sys.exit(1)

# Find the Titanium SDK
tisdk_path = ''
if not isWindows:
	tisdk_path = os.path.join('/', 'Library', 'Application Support', 'Titanium', 'mobilesdk', 'osx')
else:
	# win7
	tisdk_path = os.path.join('C:\\', 'ProgramData', 'Titanium', 'mobilesdk', 'win32')
	if not os.path.exists(tisdk_path):
		# try xp
		tisdk_path = os.path.join('C:\\', 'Documents and Settings', 'All Users', 'Application Data', 'Titanium', 'mobilesdk', 'win32')

if not os.path.exists(tisdk_path):
	print "I wanted to find titanium in %s but it's not there.  I'm confused and going home." % tisdk_path
	sys.exit(1)

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

print "Found Titanium SDK at %s" % tisdk_path

android_sdk = ''
android_sdk_check = []
if not isWindows:
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

if len(android_sdk) == 0:
	print "Could not find your android sdk folder.  Avoid this in the future by making an ANDROID_SDK env var"
	sys.exit(1)

print "Using Android sdk found at %s" % android_sdk
sys.path.append(tisdk_path)
sys.path.append(os.path.join(tisdk_path, 'android'))
import project, run

project_id = PROJECT_ID_PREFIX + project_name.lower()
args = ['python', os.path.join(tisdk_path, 'project.py'), project_name, project_id, PROJECT_FOLDER]
if isWindows:
	args.append('android')
else:
	args.extend(('iphone', 'android'))
args.append(android_sdk)

run.run(args)

guid = unicode(uuid.uuid4())

project_folder = os.path.join(PROJECT_FOLDER, project_name)
f = open(os.path.join(project_folder, 'tiapp.xml'), 'r')
tiappxml = f.read()
f.close()

p = re.compile('<guid>(.*)</guid>')
tiappxml = p.sub('<guid>' + guid + '</guid>', tiappxml)

if DISABLE_ANALYTICS:
	p = re.compile('<analytics>true</analytics>')
	tiappxml = p.sub('<analytics>false</analytics>', tiappxml)

if ENABLE_ANDROID_DEBUG:
	p = re.compile('<icon>')
	tiappxml = p.sub(ANDROID_DEBUG + '\n<icon>', tiappxml)

f = open(os.path.join(project_folder, 'tiapp.xml'), 'w')
f.write(tiappxml)
f.close()

# sqlite
conn = sqlite3.connect(tidev_db)
rows = conn.execute('select max(id) from projects')
for r in rows:
	pass
dbid = r[0] + 1

sql = """
INSERT INTO projects (id, type, guid, runtime, description, timestamp,
name, directory, appid, publisher, url, image, version, copyright)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

timestamp = time.mktime(time.localtime())
copyright = "%s by %s" % (datetime.datetime.now().year, PUBLISHER);

values = (dbid, 'mobile', guid, sdkver, "No description provided", timestamp,
		project_name, project_folder, project_id, PUBLISHER, PUBLISHER_URL, 
		'appicon.png', '1.0', copyright)
conn.execute(sql, values)
conn.commit()
conn.close()

