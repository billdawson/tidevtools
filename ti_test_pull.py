#!/usr/bin/env python
import os, sys, re, platform
import json, urllib, optparse
import zipfile
from subprocess import *

import ticommon
from tidevtools_settings import *

def git(*args):
	arglist = list(args)
	arglist.insert(0, "git")
	print " ".join(arglist)

	p = Popen(arglist)
	p.communicate()
	if p.returncode != 0:
		sys.exit(p.returncode)

def match_jira_issue(text):
	return re.match(r'TIMOB[-_]?\d+', text, re.I)

def is_jira_issue(issue):
	return match_jira_issue(issue) != None

def jira_normalize(issue):
	m = re.match(r'TIMOB(\d+)', issue, re.I)
	if m: # Missing a dash
		issue = "TIMOB-%s" % m.group(1)

	return issue.upper().replace('_', '-')

def get_issue_key(pull):
	head_ref = pull["head"]["ref"]
	issue_key = None

	if is_jira_issue(head_ref):
		issue_key = jira_normalize(head_ref)

	if issue_key == None:
		title_match = match_jira_issue(pull["title"])
		if title_match != None:
			issue_key = jira_normalize(title_match.group(0))

	return issue_key

def checkout_pull_branch(pull_number):
	pull_number = sys.argv[1]
	try:
		pull_url = "https://github.com/api/v2/json/pulls/appcelerator/titanium_mobile/%s" % pull_number
		print "Fetching Pull: %s..." % pull_url

		pull_data = urllib.urlopen(pull_url).read()
		pull = json.loads(pull_data)["pull"]

		branch = pull["head"]["ref"]
		remote = pull["head"]["repository"]["url"]
		user = pull["user"]["login"]
		issue_key = get_issue_key(pull)

		print "User: %s, Branch: %s, Remote: %s" % (user, branch, remote)

		local_branch = branch
		if issue_key == None:
			print >>sys.stderr, "Warning: No TIMOB issue found for pull %s, using supplied branch name %s" % (pull_number, branch)
		else:
			local_branch = issue_key.lower()

		# First merge w/ master
		git("checkout", TIMOBILE_MASTER)
		git("pull", TIMOBILE_ORIGIN, "master")

		# Create a local testing branch
		global test_branch
		test_branch = "%s_%s" % (user, local_branch)

		git("checkout", "-B", test_branch)
		git("pull", remote, branch)

	except Exception, e:
		print >>sys.stderr, "Error getting pull request %s: %s" % (pull_number, e)

def build_mobilesdk():
	sys.path.append(os.path.join(mobile_repo, "build"))
	import titanium_version

	global sdk_version, test_branch
	sdk_version = "%s.%s" % (titanium_version.version, test_branch)

	p = Popen(["scons", "version_tag=%s" % sdk_version], cwd=mobile_repo, shell=True)
	p.communicate()
	if p.returncode != 0:
		print >>sys.stderr, "Error Building MobileSDK"
		sys.exit(p.returncode)

def extract_mobilesdk():
	mobile_dist_dir = os.path.join(mobile_repo, 'dist')
	sys.path.append(mobile_dist_dir)
	sys.path.append(os.path.join(mobile_repo, 'build'))

	platform_name = {"Darwin": "osx", "Windows": "win32", "Linux": "linux"}[platform.system()]
	mobilesdk_dir = os.path.join(mobile_dist_dir, 'mobilesdk', platform_name, sdk_version)
	mobilesdk_zipfile = os.path.join(mobile_dist_dir, 'mobilesdk-%s-%s.zip' % (sdk_version, platform_name))
	if platform.system() == 'Darwin':
		Popen(['/usr/bin/unzip', '-q', '-o', '-d', mobile_dist_dir, mobilesdk_zipfile])
	else:
		# extract the mobilesdk zip so we can use it for testing
		mobilesdk_zip = zipfile.ZipFile(mobilesdk_zipfile)
		mobilesdk_zip.extractall(mobile_dist_dir)
		mobilesdk_zip.close()
	return mobilesdk_dir

def create_project(local_branch):
	project_script = os.path.join(mobilesdk_dir, "project.py")
	project_id = "%s.%s" % (PROJECT_ID_PREFIX.rstrip("."), local_branch)

	android_sdk = ticommon.find_android_sdk()
	project_args = [sys.executable, project_script, local_branch, project_id, PROJECT_FOLDER]

	if platform.system() == "Darwin":
		project_args.append("iphone")

	if os.path.exists(android_sdk):
		project_args.extend(["android", android_sdk])

	p = Popen(project_args)
	p.communicate()
	if p.returncode != 0:
		print >>sys.stderr, "Error creating project %s" % project_id
		sys.exit(p.returncode)

	print "Project '%s' created: %s" % (project_id, os.path.join(PROJECT_FOLDER, local_branch))

def validate_tdoc():
	validate_script = os.path.join(mobile_repo, "apidoc", "validate.py")
	p = Popen([sys.executable, validate_script])
	p.communicate()
	if p.returncode != 0:
		print >>sys.stderr, "Error Validating TDoc"
		sys.exit(p.returncode)
	else:
		print "TDoc succesfully validated"

def run_drillbit():
	# TODO: drillbit needs to be able to override the mobile sdk dir
	drillbit_script = os.path.join(mobile_repo, "drillbit", "drillbit.py")
	p = Popen([sys.executable, drillbit_script])
	p.communicate()

def main():
	parser = optparse.OptionParser(usage="%prog [options] pull-number")
	parser.add_option("-b", "--build", dest="build", default=False, action="store_true",
		help="Automatically kickoff a build of the MobileSDK zip with a suffix that matches the pull request branch / TIMOB number")
	parser.add_option("-v", "--validate", dest="validate", default=False, action="store_true",
		help="Automatically run the APIDoc validation script")
	parser.add_option("-d", "--drillbit", dest="drillbit", default=False, action="store_true",
		help="Automatically build and start Drillbit against the pull request")
	parser.add_option("-p", "--project", dest="project", default=False, action="store_true",
		help="Automatically build and create a project using PROJECT_FOLDER in tidetools_settings.py. The project name will match the branch or issue number")

	options, args = parser.parse_args()
	if len(args) == 0:
		print >>sys.stderr, "Error: missing required pull-number"
		parser.print_usage(sys.stderr)
		sys.exit(1)

	global mobile_repo
	mobile_repo = ticommon.find_mobile_repo()

	if mobile_repo == None:
		print >>sys.stderr, "You must run this script somewhere in the titanium_mobile repository"
		sys.exit(1)

	pull_number = args[0]
	checkout_pull_branch(pull_number)

	build = options.project or options.drillbit or options.build
	if build:
		build_mobilesdk()

	extract = options.project or options.drillbit
	if extract:
		global mobilesdk_dir
		mobilesdk_dir = extract_mobilesdk()

	if options.project:
		create_project()

	if options.validate:
		validate_tdoc()

	if options.drillbit:
		run_drillbit()

if __name__ == "__main__":
	main()
