#!/usr/bin/env python
"""
 * tidevtools 'ti_eclipsify' - Prepare a Titanium mobile project folder
 * for importing into Eclipse.
 *
 * Copyright (c) 2010 by Bill Dawson
 * Licensed under the terms of the Apache Public License
 * Please see the LICENSE included with this distribution for details.
 * http://github.com/billdawson/tidevtools
 *
 * Just run this script at the top of a project folder.
"""
print "tidevtools 'ti_eclipsify'"

import sys, os, platform, shutil
from os import environ as env

this_path = os.path.abspath(os.path.dirname(sys._getframe(0).f_code.co_filename))

sys.path.append(this_path)
try:
	import ticommon
except:
	print "Couldn't load ticommon from %s.  It should be sitting side-by-side with this script.  Message: &%s." % (this_path, err)
	sys.exit(1)

isWindows = ticommon.is_windows()

JARS_NEEDED = ('ti-commons-codec-1.3.jar', 'jaxen-1.1.1.jar', 'smalljs.jar')
TITANIUM_THEME="""<?xml version="1.0" encoding="utf-8"?>
<resources>
<style name="Theme.Titanium" parent="android:Theme">
    <item name="android:windowBackground">@drawable/background</item>
</style>
</resources>
"""

if not os.path.exists('tiapp.xml'):
	print "I don't see any tiapp.xml file here. \nLooks like \n%s \nis not a Titanium project folder.  Exiting..." % os.getcwd()
	sys.exit(1)

resources_folder = os.path.join('.', 'Resources')
if not os.path.exists(resources_folder):
	print "Couldn't find a Resources folder here."
	sys.exit(1)

android_folder = os.path.join('.', 'build', 'android')
if not os.path.exists(android_folder):
	print "Hmm, this looks like a Titanium Mobile project folder, but I don't see build/android. Maybe build it one time from inside Titanium Developer?"
	sys.exit(1)

assets_folder = os.path.join(android_folder,'assets')
if not os.path.exists(assets_folder):
	os.mkdir(assets_folder)

appid = ticommon.get_appid('.')

gen_folder =os.path.join(android_folder, 'gen', ticommon.appid_to_path(appid))
if not os.path.exists(gen_folder):
	os.makedirs(gen_folder)
	print "Created %s" % gen_folder

src_folder = os.path.join(android_folder, 'src', ticommon.appid_to_path(appid))
r_file = os.path.join(src_folder, 'R.java')
if os.path.exists(r_file):
	shutil.copyfile(r_file, os.path.join(gen_folder, 'R.java'))
	os.remove(r_file)
	print 'Moved R.java to "gen" folder'

if isWindows:
	print "Copying Resources and tiapp.xml to assets folder because you're running Windows and therefore we're not going to make symlinks"
	shutil.copytree(resources_folder, os.path.join(assets_folder, 'Resources'))
	shutil.copy(os.path.join('.', 'tiapp.xml'), assets_folder)
else:
	resources_dest = os.path.abspath(os.path.join(assets_folder, 'Resources'))
	tiapp_dest = os.path.abspath(os.path.join(assets_folder, 'tiapp.xml'))
	if not os.path.exists(resources_dest):
		os.symlink(os.path.abspath(resources_folder), resources_dest)
		print 'Symlinked Resources to assets/Resources'
	if not os.path.exists(tiapp_dest):
		os.symlink(os.path.abspath(os.path.join('.', 'tiapp.xml')), tiapp_dest)
		print 'Symlinked tiapp.xml to assets/tiapp.xml'

cpath_additions = """
<classpathentry combineaccessrules="false" kind="src" path="/titanium"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-accelerometer"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-analytics"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-api"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-app"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-database"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-facebook"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-filesystem"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-geolocation"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-gesture"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-json"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-map"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-media"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-network"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-platform"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-ui"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-utils"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-xml"/>
<classpathentry combineaccessrules="false" kind="src" path="/titanium-yahoo"/>
<classpathentry kind="lib" path="lib/ti-commons-codec-1.3.jar"/>
<classpathentry kind="lib" path="lib/jaxen-1.1.1.jar"/>
<classpathentry kind="lib" path="lib/smalljs.jar"/>
"""
cpath_additions = cpath_additions.split('\n')
if ticommon.ti_module_exists('titanium-contacts'):
	cpath_additions.append('<classpathentry combineaccessrules="false" kind="src" path="/titanium-contacts"/>')

if ticommon.ti_module_exists('titanium-calendar'):
	cpath_additions.append('<classpathentry combineaccessrules="false" kind="src" path="/titanium-calendar"/>')

if ticommon.ti_module_exists('titanium-bump'):
	cpath_additions.append('<classpathentry combineaccessrules="false" kind="src" path="/titanium-bump"/>')

if ticommon.ti_module_exists('titanium-android'):
	cpath_additions.append('<classpathentry combineaccessrules="false" kind="src" path="/titanium-android"/>')
	# if that's there then so is the localization one.
	cpath_additions.append('<classpathentry combineaccessrules="false" kind="src" path="/titanium-i18n"/>')


cpath = os.path.join(android_folder, '.classpath')
if os.path.exists(cpath):
	f = open(cpath, 'r')
	lines_out = []
	already_added_projects = False
	modified = False
	for line in f:
		skip = False
		if 'titanium.jar' in line:
			modified = True
			skip = True
		if 'titanium-ui' in line:
			already_added_projects = True
		if '</classpath>' in line and not already_added_projects:
			# write the stuff  we want before it closes
			modified = True
			lines_out.extend(cpath_additions)
		if not skip:
			lines_out.append(line)

	f.close()

	if modified:
		f = open(cpath, 'w')
		f.write( '\n'.join(lines_out) )
		f.close()
		print 'Modified .classpath'
else:
	print "Couldn't find %s. Continuing..." % cpath

if not os.path.exists(os.path.join(android_folder, 'gen')):
	os.mkdir(os.path.join(android_folder, 'gen'))
	print 'Made a "gen" folder'

lib_folder = os.path.join(android_folder, 'lib')
if not os.path.exists(lib_folder):
	os.mkdir(lib_folder)
	print 'Made a "lib" folder'

tisdk = ticommon.find_ti_sdk()[0]
if len(tisdk) > 0:
	for jar in JARS_NEEDED:
		if not os.path.exists(os.path.join(lib_folder, jar)):
			if os.path.exists(os.path.join(tisdk, 'android', jar)):
				shutil.copy(os.path.join(tisdk, 'android', jar), os.path.join(lib_folder, jar))
				print 'Copied over %s' % jar
else:
	print 'Could not locate Titanium SDK folder, so did not copy over any of the required jars like js.jar'

res_folder = os.path.join(android_folder, 'res')
if not os.path.exists(res_folder):
	os.mkdir(res_folder)
	print 'Made a "res" folder'

drawable_folder = os.path.join(res_folder, 'drawable')
if not os.path.exists(drawable_folder):
	os.mkdir(drawable_folder)
	print 'Made a "res/drawable" folder'

values_folder = os.path.join(res_folder, 'values')
if not os.path.exists(values_folder):
	os.mkdir(values_folder)
	print 'Made a "res/values" folder'

if not os.path.exists(os.path.join(values_folder, 'theme.xml')):
	f = open(os.path.join(values_folder, 'theme.xml'), 'w')
	f.write(TITANIUM_THEME)
	f.close()
	print 'Wrote the theme.xml file'

if not os.path.exists(os.path.join(drawable_folder, 'appicon.png')):
	if len(tisdk) > 0:
		if os.path.exists(os.path.join(tisdk, 'android', 'resources', 'appicon.png')):
			shutil.copy(os.path.join(tisdk, 'android', 'resources', 'appicon.png'), drawable_folder)
			print 'Copied over appicon.png to res/drawables'

if not os.path.exists(os.path.join(drawable_folder, 'background.png')):
	if len(tisdk) > 0:
		if os.path.exists(os.path.join(tisdk, 'android', 'resources', 'default.png')):
			shutil.copy(os.path.join(tisdk, 'android', 'resources', 'default.png'), os.path.join(drawable_folder, 'background.png'))
			print 'Copied over default.png to res/drawables/background.png'

# put debuggable=true in manifest so you can do phone debugging
import codecs, re
f = codecs.open(os.path.join(android_folder, 'AndroidManifest.xml'), 'r', 'utf-8')
xml = f.read()
f.close()
xml = re.sub(r'android\:debuggable="false"', 'android:debuggable="true"', xml)
f = codecs.open(os.path.join(android_folder, 'AndroidManifest.xml'), 'w', 'utf-8')
f.write(xml)



print "Done."
