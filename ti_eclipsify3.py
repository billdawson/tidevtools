#!/usr/bin/env python
"""
 * tidevtools 'ti_eclipsify3' - Prepare a Titanium mobile 1.8.0+ project folder
 * for importing into Eclipse.
 *
 * Copyright (c) 2010-2011 by Bill Dawson
 * Licensed under the terms of the Apache Public License
 * Please see the LICENSE included with this distribution for details.
 * http://github.com/billdawson/tidevtools
 *
 * Just run this script at the top of a project folder.
"""
import sys, os, platform, shutil
from os import environ as env
from subprocess import call

this_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(this_path)
try:
	import ticommon
except:
	print >> sys.stderr, "[ERROR] Couldn't load ticommon from %s.  It should be sitting side-by-side with this script.  Message: &%s." % (this_path, err)
	sys.exit(1)

tisdk = ticommon.find_ti_sdk()[0]
if not os.path.exists(tisdk):
	print >> sys.stderr, "[ERROR] Couldn't locate your Titanium Mobile sdk folder.  Please set a TI_DEV_SDK environment variable with the path to the the latest version of the Titanium Mobile SDK."
	sys.exit(1)

sys.path.append(os.path.join(tisdk, "android"))
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
required_folders = (android_folder,
		os.path.join(assets_folder),
		os.path.join(android_folder, "res"),
		os.path.join(android_folder, "gen"))

for required in required_folders:
	if not os.path.exists(required):
		log.error("You need to build your project one time with Titanium Studio before 'eclipsifying' it.")
		sys.exit(1)

is_windows = ticommon.is_windows()

############## DEFAULTS ########################
# Put a file named tidevtools_settings.py in the 
# same folder as this file, then you can override this
ECLIPSE_PROJ_BOOTSTRAP_PATH = '' # /e.g., /Users/bill/projects/ti_eclipse_project_defaults
TIMOBILE_SRC = ''
#################################################
if os.path.exists(os.path.join(this_path, 'tidevtools_settings.py')):
	execfile(os.path.join(this_path, 'tidevtools_settings.py'))

# To make sure rhino works, move kroll-rhino-bindings.jar and
# kroll-rhino-js.jar into libs
libs_folder = os.path.join(android_folder, "libs")
if not os.path.exists(libs_folder):
	os.mkdir(libs_folder)
rhino_bindings = os.path.join(libs_folder, "kroll-rhino-bindings.jar")
rhino_js = os.path.join(libs_folder, "kroll-rhino-js.jar")
if not os.path.exists(rhino_bindings):
	shutil.copyfile(os.path.join(TIMOBILE_SRC, "dist", "android", "kroll-rhino-bindings.jar"), rhino_bindings)
if not os.path.exists(rhino_js):
	shutil.copyfile(os.path.join(TIMOBILE_SRC, "dist", "android", "kroll-rhino-js.jar"), rhino_js)

if (ECLIPSE_PROJ_BOOTSTRAP_PATH is None or len(ECLIPSE_PROJ_BOOTSTRAP_PATH) == 0 or
		not os.path.exists(ECLIPSE_PROJ_BOOTSTRAP_PATH)):
	log.error("ECLIPSE_PROJ_BOOTSTRAP_PATH setting not set property: %s" % ECLIPSE_PROJ_BOOTSTRAP_PATH)
	sys.exit(1)

appid = ticommon.get_appid('.')
app_info = ticommon.get_app_info('.')
appid = app_info["id"]
project_name = app_info["name"]

gen_folder =os.path.join(android_folder, 'gen', ticommon.appid_to_path(appid))
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

# Remove all code for starting up the debugger.
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

if is_windows:
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

# put debuggable=true in manifest so you can do device debugging. 
import codecs, re
f = codecs.open(os.path.join(android_folder, 'AndroidManifest.xml'), 'r', 'utf-8')
xml = f.read()
f.close()
xml = re.sub(r'android\:debuggable="false"', 'android:debuggable="true"', xml)
f = codecs.open(os.path.join(android_folder, 'AndroidManifest.xml'), 'w', 'utf-8')
f.write(xml)

# Copy .classpath, .project, default.properties from your bootstrap folder.
log.trace("Copying .classpath, .project, default.properties from %s" % ECLIPSE_PROJ_BOOTSTRAP_PATH)
shutil.copyfile(os.path.join(ECLIPSE_PROJ_BOOTSTRAP_PATH, ".classpath"),
		os.path.join(android_folder, ".classpath"))
#shutil.copyfile(os.path.join(ECLIPSE_PROJ_BOOTSTRAP_PATH, "default.properties"),
#		os.path.join(android_folder, "default.properties"))
shutil.copyfile(os.path.join(ECLIPSE_PROJ_BOOTSTRAP_PATH, ".project"),
		os.path.join(android_folder, ".project"))
shutil.copyfile(os.path.join(ECLIPSE_PROJ_BOOTSTRAP_PATH, "project.properties"),
		os.path.join(android_folder, "project.properties"))
f = codecs.open(os.path.join(android_folder, '.project'), 'r', 'utf-8')
project_xml = f.read()
f.close()
project_xml = project_xml.replace("[PROJECT_NAME]", project_name)
f = codecs.open(os.path.join(android_folder, '.project'), 'w', 'utf-8')
f.write(project_xml)
f.close()

