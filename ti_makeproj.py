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

import sys, os, uuid, re, time, datetime, subprocess, shutil
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
MANIFEST_TEMPLATE="""#appname: %project_name%
#publisher: %PUBLISHER%
#url: %PUBLISHER_URL%
#image: appicon.png
#appid: %project_id%
#desc: undefined
#type: mobile
#guid: %guid%
"""

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

def replace_tokens_string(input):
	result_list = replace_tokens( [ input ] )
	return result_list[0]

simulation = False
if len(sys.argv) < 2:
	print "Usage: %s <name>" % os.path.basename(sys.argv[0])
	sys.exit(1)

if len(sys.argv) > 2:
	argstring = ' '.join(sys.argv)
	simulation = '--simulate' in argstring

this_path = os.path.abspath(os.path.dirname(sys._getframe(0).f_code.co_filename))

sys.path.append(this_path)
try:
	import ticommon
except Exception, err:
	print "Couldn't load ticommon from %s.  It should be sitting side-by-side with this script.  Message: %s." % (this_path, err)
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
	args.append('android', 'mobileweb')
else:
	args.extend(('iphone', 'android', 'mobileweb'))
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

	if PUBLISHER:
		p = re.compile('<publisher>not specified</publisher>')
		tiappxml = p.sub('<publisher>' + PUBLISHER + '</publisher>', tiappxml)
		p = re.compile('<copyright>not specified</copyright>')
		tiappxml = p.sub('<copyright>%s by %s</copyright>' % (str(datetime.datetime.now().year), PUBLISHER), tiappxml)

	if PUBLISHER_URL:
		p = re.compile('<url>not specified</url>')
		tiappxml = p.sub('<url>%s</url>' % PUBLISHER_URL, tiappxml)

	f = open(os.path.join(project_folder, 'tiapp.xml'), 'w')
	f.write(tiappxml)
	f.close()
	f = open(os.path.join(project_folder, 'manifest'), 'w')
	f.write(replace_tokens_string(MANIFEST_TEMPLATE))
	f.close()
else:
	print "SIMULATION - Would open the new tiapp.xml file, change the guid,  write out the manifest, etc."

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
				print "SIMULATION - Would copy files from %s to %s" % (template_folder, project_folder)
			else:
				for root, dirs, files in os.walk(template_folder):
					for f in files:
						orig = os.path.join(root, f)
						orig_rel = orig.replace(template_folder,'')
						if orig_rel.startswith(os.sep):
							orig_rel = orig_rel[1:]
						dest = os.path.join(project_folder, orig_rel)
						if not os.path.exists(os.path.dirname(dest)):
							os.makedirs(os.path.dirname(dest))
						print "Copying %s -> %s" % (orig, dest)
						shutil.copy(orig, dest)

if EXEC_AT_END:
	if not simulation:
		subprocess.Popen(replace_tokens(EXEC_AT_END))
	else:
		print "SIMULATION - Would have run %s" % " ".join(replace_tokens(EXEC_AT_END))
	

print 'Done'
