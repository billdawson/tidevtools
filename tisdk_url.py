#!/usr/bin/env python
import sys, urllib, simplejson

if len(sys.argv) == 1:
	print "Usage: %s <version>" % sys.argv[0]
	sys.exit(1)

version = sys.argv[1]
data = simplejson.loads(urllib.urlopen('http://api.appcelerator.net/p/v1/release-list').read())

print 'URLs for Version %s:' % version
for release in data["releases"]:
	if release["version"] == version:
		print '    %s (%s): %s' % (release["os"], release["build_type"], release["url"])
