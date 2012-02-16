#!/usr/bin/env python

# To run this you should set the ANDROID_SDK environment
# variable to point to the root of the Android SDK installation
# directory. Mine points to
# /opt/android-sdk-mac_86

# ti_builder.py
# Run this from the root directory of a Titanium project
# (the directory containing tiapp.xml)

import os, sys, platform, subprocess
import ticommon

projectPath = os.path.abspath(os.getcwd())

tiappXML = os.path.join(projectPath, 'tiapp.xml')
timoduleXML = os.path.join(projectPath, 'timodule.xml')

def error(msg):
	print >>sys.stderr, "Error: " + msg
	sys.exit(1)

if not (os.path.exists(tiappXML) or os.path.exists(timoduleXML)):
	error("No tiapp.xml/timodule.xml found, are you in a Titanium project?")

androidSDK = ticommon.find_android_sdk()

if not os.path.exists(androidSDK):
	error("Android SDK directory doesn't exist: %s" % androidSDK)

if 'TI_VERSION' in os.environ:
	tiDevSDK = ticommon.find_ti_sdk(version=os.environ['TI_VERSION'])[0]
else:
	tiDevSDK = ticommon.find_ti_sdk()[0]

if not os.path.exists(tiDevSDK):
	error("Titanium Mobile SDK directory doesn't exist: %s" % tiDevSDK)

builderScript = os.path.join(tiDevSDK, 'android', 'builder.py')

if not os.path.exists(builderScript):
	error("Builder script doesn't exist: %s" % builderScript)

appInfo = ticommon.get_app_info(projectPath)
name = appInfo['name']
id = appInfo['id']

command = 'build'
debug = False

if len(sys.argv) > 1:
	if sys.argv[1] == 'debug':
		del sys.argv[1]
		debug = True
	if len(sys.argv) > 1:
		command = sys.argv[1]

args = [sys.executable]
if debug:
	args.append('-mpdb')

if command == 'generate':
	androidScript = os.path.join(tiDevSDK, 'android', 'android.py')
	args.extend([androidScript, name, id, os.path.dirname(projectPath), androidSDK])
else:
	if command == 'run' and os.path.exists(timoduleXML): # running a module project
		moduleBuilderScript = os.path.join(tiDevSDK, 'module', 'builder.py')
		args.extend([moduleBuilderScript, command, 'android', projectPath])
	else:
		args.extend([builderScript, command, name, androidSDK, projectPath, id])

# AVD arg support for emulator / simulator / install
# 7 / HVGA reasonable defaults?
# Override with TI_AVD_ID / TI_AVD_SKIN
avdID = '7'
if 'TI_AVD_ID' in os.environ:
	avdID = os.environ['TI_AVD_ID']

avdSkin = 'HVGA'
if 'TI_AVD_SKIN' in os.environ:
	avdSkin = os.environ['TI_AVD_SKIN']

if command in ['emulator', 'simulator', 'install']:
	if len(sys.argv) > 2:
		avdID = sys.argv[2]
	print 'Using AVD ID: %s' % avdID
	args.append(avdID)

	if command == 'emulator':
		if len(sys.argv) > 3:
			avdSkin = sys.argv[3]
		print 'Using AVD Skin: %s' % avdSkin
		args.append(avdSkin)

if command == 'distribute':
	if len(sys.argv) < 6:
		error('"distribute" requires at least 4 args:\n\tti_builder.py distribute <keystore> <password> <alias> <output dir> [<avd id>]')
	args.extend(sys.argv[2:])
	if len(sys.argv) == 6:
		args.append(avdID)

print '%s' % subprocess.list2cmdline(args)
os.execv(sys.executable, args)
