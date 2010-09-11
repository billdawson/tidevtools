#!/usr/bin/env python
"""
 * tidevtools 'ti_makeproj' - create a Titanium Mobile Project
 *
 * Copyright (c) 2010 by Bill Dawson
 * Licensed under the terms of the Apache Public License
 * Please see the LICENSE included with this distribution for details.
 * http://github.com/billdawson/tidevtools
 *
 * So just pass it a project name, it'll do the rest.  But first 
 * be sure to create a tidevtools_settings.py file in this same 
 * folder and override the values for the "constants" you see below.
"""
print "tidevtools 'ti_makeproj'"

import sys, os, uuid, re, sqlite3, time, datetime, subprocess, shutil
from os import environ as env

############## DEFAULTS ########################
# Put a file named tidevtools_settings.py in the 
# same folder as this file, then you can override all of these
PROJECT_ID_PREFIX = '' # e.g., com.billdawson.
PROJECT_FOLDER = '' # e.g., /Users/bill/projects/ti
PUBLISHER = '' # e.g., Bill Dawson
PUBLISHER_URL = '' # e.g., billdawson.com
DISABLE_ANALYTICS = True
ENABLE_ANDROID_DEBUG = True
EXEC_AT_END = [] # arglist for Popen, e.g. ['mvim', '--cmd', 'cd %project_folder%']
#################################################
ANDROID_DEBUG = '<property type="bool" name="ti.android.debug">true</property>'

simulation = False
no_db = False
if len(sys.argv) < 2:
	print "Usage: %s <name>" % os.path.basename(sys.argv[0])
	sys.exit(1)

if len(sys.argv) > 2:
	argstring = ' '.join(sys.argv)
	simulation = '--simulate' in argstring
	no_db = '--nodb' in argstring

this_path = os.path.abspath(os.path.dirname(sys._getframe(0).f_code.co_filename))

sys.path.append(this_path)
try:
	import ticommon
except:
	print "Couldn't load ticommon from %s.  It should be sitting side-by-side with this script.  Message: &%s." % (this_path, err)
	sys.exit(1)

if os.path.exists(os.path.join(this_path, 'tidevtools_settings.py')):
	execfile(os.path.join(this_path, 'tidevtools_settings.py'))

if not PROJECT_ID_PREFIX or not PROJECT_FOLDER or not PUBLISHER or not PUBLISHER_URL:
	print 'You need to fill in PROJECT_ID_PREFIX and all that.  Use a file named tidevtools_settings.py'
	sys.exit(1)

project_name = sys.argv[1]
project_folder = os.path.join(PROJECT_FOLDER, project_name)
resources_folder = os.path.join(project_folder, 'Resources')
if os.path.exists(project_folder):
	print "%s already exists." % project_folder
	sys.exit(1)

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

if not simulation:
	run.run(args)
else:
	print "SIMULATION - Would have run %s" % " ".join(args)

guid = unicode(uuid.uuid4())

if not simulation:
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
else:
	print "SIMULATION - Would open the new tiapp.xml file, change the guid, etc."

# sqlite
if not simulation and not no_db:
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
else:
	print "SIMULATION - Would create an entry in the Titanium Developer Sqlite database"

# Base the project on a template?
template_folder = os.path.join(PROJECT_FOLDER, 'templates')
template = ''
if os.path.exists(template_folder):
	templates = [d for d in os.listdir(template_folder) if os.path.isdir(os.path.join(template_folder, d))]
	print '\nChoose a template or just hit enter to use titanium default:\n'
	for i in range(0, len(templates)):
		print '%s\t%s\n' % (i, templates[i])
	choice = raw_input('Make your selection: ')
	if not choice:
		print 'Sticking with default'
	else:
		try:
			choice = int(choice)
			if choice >= len(templates):
				print 'Invalid choice ignored'
			else:
				template = templates[choice]
		except Exception, err:
			print 'Failed to read your choice: %s' % err
		if template:
			print 'You selected the "%s" template' % template
			template_folder = os.path.join(template_folder, template)
			if simulation:
				print "SIMULATION - Would copy files from %s to %s" % (template_folder, resources_folder)
			else:
				for root, dirs, files in os.walk(template_folder):
					for f in files:
						orig = os.path.join(root, f)
						orig_rel = orig.replace(template_folder,'')
						if orig_rel.startswith(os.sep):
							orig_rel = orig_rel[1:]
						dest = os.path.join(resources_folder, orig_rel)
						if not os.path.exists(os.path.dirname(dest)):
							os.makedirs(os.path.dirname(dest))
						print "Copying %s -> %s" % (orig, dest)
						shutil.copy(orig, dest)

def replace_tokens(input):
	result = []
	pattern = r"(%\S+%)"
	for item in input:
		newitem = item
		tokens = re.findall(pattern, newitem)
		if tokens:
			for token in tokens:
				if token.replace('%', '') in globals():
					newitem = newitem.replace(token, globals()[token.replace('%', '')])
		result.append(newitem)
	return result

if EXEC_AT_END:
	if not simulation:
		subprocess.Popen(replace_tokens(EXEC_AT_END))
	else:
		print "SIMULATION - Would have run %s" % " ".join(replace_tokens(EXEC_AT_END))
	

print 'Done'
