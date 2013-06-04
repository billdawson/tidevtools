#!/usr/bin/env python
"""
 * tidevtools 'ti_eclipsify' - Prepare a Titanium mobile 1.8.0+ project folder
 * for importing into Eclipse.
 *
 * Copyright (c) 2010-2012 by Bill Dawson
 * Licensed under the terms of the Apache Public License
 * Please see the LICENSE included with this distribution for details.
 * http://github.com/billdawson/tidevtools
 *
 * Just run this script at the top of a project folder.
 * See ti_eclipsify.md for more details.
"""

import sys, os, shutil

# Contents for Eclipse/ADT required project files.
project_properties="""target=android-17
apk-configurations=
android.library.reference.1=../android/titanium
android.library.reference.2=../android/modules/accelerometer
android.library.reference.3=../android/modules/analytics
android.library.reference.4=../android/modules/android
android.library.reference.5=../android/modules/app
android.library.reference.6=../android/runtime/common
android.library.reference.7=../android/runtime/v8
android.library.reference.8=../android/modules/calendar
android.library.reference.9=../android/modules/contacts
android.library.reference.10=../android/modules/database
android.library.reference.11=../android/modules/geolocation
android.library.reference.12=../android/modules/filesystem
android.library.reference.13=../android/modules/gesture
android.library.reference.14=../android/modules/locale
android.library.reference.15=../android/modules/map
android.library.reference.16=../android/modules/media
android.library.reference.17=../android/modules/network
android.library.reference.18=../android/modules/platform
android.library.reference.19=../android/modules/ui
android.library.reference.20=../android/modules/utils
android.library.reference.21=../android/modules/xml
"""
dot_classpath="""<?xml version="1.0" encoding="UTF-8"?>
<classpath>
  <classpathentry kind="src" path="src"/>
  <classpathentry kind="src" path="gen"/>
  <classpathentry kind="con" path="com.android.ide.eclipse.adt.ANDROID_FRAMEWORK"/>
  <classpathentry exported="true" kind="con" path="com.android.ide.eclipse.adt.LIBRARIES"/>
  <classpathentry kind="lib" path="/titanium/lib/commons-logging-1.1.1.jar"/>
  <classpathentry kind="lib" path="/titanium/lib/ti-commons-codec-1.3.jar"/>
  <classpathentry kind="lib" path="/titanium-dist/lib/kroll-apt.jar"/>
  <classpathentry kind="lib" path="/titanium-xml/lib/jaxen-1.1.1.jar"/>
  <classpathentry kind="lib" path="/titanium/lib/android-support-v4.jar"/>
  <classpathentry kind="lib" path="/titanium/lib/thirdparty.jar"/>
  <classpathentry kind="output" path="bin/classes"/>
</classpath>
"""
dot_project="""<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
	<name>[PROJECT_NAME]</name>
	<comment></comment>
	<projects>
	</projects>
	<buildSpec>
		<buildCommand>
			<name>com.android.ide.eclipse.adt.ResourceManagerBuilder</name>
			<arguments>
			</arguments>
		</buildCommand>
		<buildCommand>
			<name>com.android.ide.eclipse.adt.PreCompilerBuilder</name>
			<arguments>
			</arguments>
		</buildCommand>
		<buildCommand>
			<name>org.eclipse.jdt.core.javabuilder</name>
			<arguments>
			</arguments>
		</buildCommand>
		<buildCommand>
			<name>com.android.ide.eclipse.adt.ApkBuilder</name>
			<arguments>
			</arguments>
		</buildCommand>
	</buildSpec>
	<natures>
		<nature>com.android.ide.eclipse.adt.AndroidNature</nature>
		<nature>org.eclipse.jdt.core.javanature</nature>
	</natures>
</projectDescription>
"""

this_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(this_path)
try:
	import ticommon
except:
	print >> sys.stderr, "[ERROR] Couldn't load ticommon from %s.  It should be sitting side-by-side with this script.  Message: &%s." % (this_path, err)
	sys.exit(1)

############## DEFAULTS ########################
# Put a file named tidevtools_settings.py in the
# same folder as this file, then you can override this
TIMOBILE_SRC = ''
#################################################

if os.path.exists(os.path.join(this_path, 'tidevtools_settings.py')):
	execfile(os.path.join(this_path, 'tidevtools_settings.py'))

if not os.path.exists(TIMOBILE_SRC):
	print >> sys.stderr, "[ERROR] Could not locate the Titanium Mobile SDK sources. Please create a 'tidevtools_settings.py' in the same folder as this script file and add a string variable named TIMOBILE_SRC which is set to the path where the Titanium Mobile SDK sources are located."
	sys.exit(1)

sys.path.append(os.path.join(TIMOBILE_SRC, "support", "android"))
from tilogger import *
log = TiLogger(None, level=TiLogger.INFO)

if not os.path.exists('tiapp.xml'):
	log.error("I don't see any tiapp.xml file here. \nLooks like \n%s \nis not a Titanium project folder.  Exiting..." % os.getcwd())
	sys.exit(1)

resources_folder = os.path.join('.', 'Resources')
if not os.path.exists(resources_folder):
	log.error("Couldn't find a Resources folder here.")
	sys.exit(1)

android_folder = os.path.join('.', 'build', 'android')

assets_folder = os.path.join(android_folder, 'assets')
bin_assets_folder = os.path.join(android_folder, "bin", "assets")
libs_folder = os.path.join(android_folder, "libs")
required_folders = (android_folder,
		os.path.join(assets_folder),
		os.path.join(android_folder, "res"),
		os.path.join(android_folder, "gen"))

for required in required_folders:
	if not os.path.exists(required):
		log.error("You need to build your project one time with Titanium Studio before 'eclipsifying' it.")
		sys.exit(1)

# For V8, copy required native libraries to libs/
if not os.path.exists(libs_folder):
	os.makedirs(libs_folder)
""" Apparently not required anymore
src_libs_dir = os.path.join(TIMOBILE_SRC, "dist", "android", "libs")
if os.path.exists(src_libs_dir):
	for root, dirs, files in os.walk(src_libs_dir):
		for filename in files:
			full_path = os.path.join(root, filename)
			rel_path = os.path.relpath(full_path, src_libs_dir)
			dest_file = os.path.join(os.path.abspath(libs_folder), rel_path)
			if not os.path.exists(dest_file):
				if not os.path.exists(os.path.dirname(dest_file)):
					os.makedirs(os.path.dirname(dest_file))
				shutil.copyfile(full_path, dest_file)
"""

app_info = ticommon.get_app_info('.')
appid = app_info["id"]
project_name = app_info["name"]

gen_folder = os.path.join(android_folder, 'gen', ticommon.appid_to_path(appid))
if not os.path.exists(gen_folder):
	os.makedirs(gen_folder)

src_folder = os.path.abspath(os.path.join(android_folder, 'src', ticommon.appid_to_path(appid)))
r_file = os.path.join(src_folder, 'R.java')
if os.path.exists(r_file):
	shutil.copyfile(r_file, os.path.join(gen_folder, 'R.java'))
	os.remove(r_file)

# put everything that's in gen/, except R.java, into src/. Eclipse (or the ADT plugin, whatever)
# likes to cleanout the gen/ folder when building, which is really annoying when suddenly all of
# our generated classes disappear.
gen_files = [x for x in os.listdir(gen_folder) if x != 'R.java' and x.endswith('.java')]
if gen_files:
	if not os.path.exists(src_folder):
		os.makedirs(src_folder)
	for one_gen_file in gen_files:
		shutil.copyfile(os.path.join(gen_folder, one_gen_file), os.path.join(src_folder, one_gen_file))
		os.remove(os.path.join(gen_folder, one_gen_file))

# Get rid of calls to TiVerify in the Application.java
application_java = [f for f in gen_files if f.endswith("Application.java")]
if application_java:
	application_java = os.path.abspath(os.path.join(src_folder, application_java[0]))
	lines = open(application_java, 'r').readlines()
	lines = [l for l in lines if "TiVerify" not in l and "verify.verify" not in l]
	open(application_java, "w").write("".join(lines))

# To avoid the Android 2373 warning, set special property in AppInfo.java
appinfo_java = [f for f in gen_files if f.endswith("AppInfo.java")]
if appinfo_java:
	appinfo_java = os.path.abspath(os.path.join(src_folder, appinfo_java[0]))
	lines = open(appinfo_java, 'r').readlines()
	lines_out = []
	for l in lines:
		if l.endswith("app.getAppProperties();\n"):
			lines_out.append(l)
			lines_out.append('\t\t\t\t\tproperties.setBool("ti.android.bug2373.disableDetection", true);\n')
			lines_out.append('\t\t\t\t\tappProperties.setBool("ti.android.bug2373.disableDetection", true);\n')
		else:
			lines_out.append(l)
	with open(appinfo_java, 'w') as f:
		f.write("".join(lines_out))

# Remove all code for starting up the Javascript debugger.
if application_java:
	lines = open(application_java, 'r').readlines()
	lines = [l for l in lines if "debug" not in l.lower()]
	open(application_java, "w").write("".join(lines))

# if bin/assets/app.json is there, copy it to assets/app.json
if os.path.exists(os.path.join(bin_assets_folder, "app.json")):
	shutil.copyfile(os.path.join(bin_assets_folder, "app.json"), os.path.join(assets_folder, "app.json"))

# if bin/assets/index.json is there, copy it to assets/index.json
if os.path.exists(os.path.join(bin_assets_folder, "index.json")):
	shutil.copyfile(os.path.join(bin_assets_folder, "index.json"), os.path.join(assets_folder, "index.json"))

if ticommon.is_windows():
	log.info("Copying Resources and tiapp.xml to assets folder because you're running Windows and therefore we're not going to make symlinks")
	shutil.copytree(resources_folder, os.path.join(assets_folder, 'Resources'))
	shutil.copy(os.path.join('.', 'tiapp.xml'), assets_folder)
else:
	resources_dest = os.path.abspath(os.path.join(assets_folder, 'Resources'))
	tiapp_dest = os.path.abspath(os.path.join(assets_folder, 'tiapp.xml'))
	if not os.path.exists(resources_dest):
		os.symlink(os.path.abspath(resources_folder), resources_dest)
	if not os.path.exists(tiapp_dest):
		os.symlink(os.path.abspath(os.path.join('.', 'tiapp.xml')), tiapp_dest)

# put debuggable=true in Android manifest so you can do device debugging.
import codecs, re
f = codecs.open(os.path.join(android_folder, 'AndroidManifest.xml'), 'r', 'utf-8')
xml = f.read()
f.close()
xml = re.sub(r'android\:debuggable="false"', 'android:debuggable="true"', xml)
f = codecs.open(os.path.join(android_folder, 'AndroidManifest.xml'), 'w', 'utf-8')
f.write(xml)

# Write the required Eclipse/ADT .project, .classpath and project.properties files.
f = codecs.open(os.path.join(android_folder, ".classpath"), "w")
f.write(dot_classpath)
f.close()

f = codecs.open(os.path.join(android_folder, ".project"), "w")
f.write(dot_project.replace("[PROJECT_NAME]", project_name))
f.close()

f = codecs.open(os.path.join(android_folder, "project.properties"), "w")
f.write(project_properties)
f.close()

# Fixup Android library project paths in project.properties
props_file = os.path.join(android_folder, "project.properties")
f = codecs.open(props_file, 'r', 'utf-8')
lines = f.readlines()
newlines = []
f.close()

for line in lines:
	if not line.startswith('android.library.reference'):
		newlines.append(line)
		continue

	# Special case: the titanium module is only one folder
	# down from "android" (other modules are two folders down)
	titanium_module = "android%stitanium" % os.sep
	if line.strip().endswith(titanium_module):
		rel_path = titanium_module
	else:
		rel_path = os.sep.join(line.strip().split(os.sep)[-3:])
	if not rel_path.startswith("android"):
		newlines.append(line)
		continue
	full_path = os.path.join(TIMOBILE_SRC, rel_path)
	if not os.path.exists(full_path):
		newlines.append(line)
		continue
	newlines.append("%s=%s\n" % (line.split("=")[0], os.path.relpath(full_path, android_folder)))

f = codecs.open(props_file, 'w', 'utf-8')
f.write("".join(newlines))
f.close()

