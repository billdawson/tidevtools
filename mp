#!/usr/bin/env python
"""
 * tidevtools 'mp' - create a Titanium Mobile Project
 *
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

this_path = os.path.abspath(os.path.dirname(sys._getframe(0).f_code.co_filename))

sys.path.append(this_path)
try:
	import ticommon
except:
	print "Couldn't load ticommon from %s.  It should be sitting side-by-side with this script.  Message: &%s." % (this_path, err)
	sys.exit(1)


project_name = sys.argv[1]
isWindows = ticommon.is_windows()
tidev_db = ticommon.find_ti_dev_db()

if len(tidev_db) == 0:
	print "I couldn't find your Titanium Developer sqlite db."
	sys.exit(1)

# Find the Titanium SDK
tisdk_path, sdkver = ticommon.find_ti_sdk()
if len(tisdk_path) == 0 or not os.path.exists(tisdk_path):
	print "I couldn't find the Titanium Mobile SDK"
	sys.exit(1)

print "Found Titanium SDK at %s" % tisdk_path

android_sdk = ticommon.find_android_sdk()
if len(android_sdk) == 0 or not os.path.exists(android_sdk):
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

os.chdir(project_folder)
