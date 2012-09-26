#!/usr/bin/env python
import zipfile, os, sys
import json, urllib


TI_CLOUD = ("2.3.0", "2.3.0") # old versus new
TI_CLOUD_PUSH = ("2.0.7", "2.0.7") # old versus new
SDK_VER = ("2.1.2.GA", "2.1.3") # old versus new

"""
Steps:
* Fill in the TI_CLOUD, TI_CLOUD_PUSH and SDK_VER lists above.
* Package all platform zips using "scons package_all=1".
* Copy the three zip files (under dist/) to the folder indicated by DIR below.
* Run this file.
* Look in "osx-results.txt", etc., to see any differences between the contents of the old
and new zip files. If anything looks funny, investigate.
* If everything looks good, give the three newer .bom files to QE.
"""

DIR = "/Users/bill/tmp/compare"
PLATFORMS = ("osx", "win32", "linux")
REL_LIST_URL = "http://api.appcelerator.net/p/v1/release-list"

def download_status(blocks_so_far, block_size, file_size):
	bytes_so_far = blocks_so_far * block_size
	if bytes_so_far % 1000 == 0:
		sys.stdout.write(".")
		sys.stdout.flush()


def get_old_zips():
	download_info = None
	for p in PLATFORMS:
		zip_file = os.path.join(DIR, "mobilesdk-%s-%s.zip" % (SDK_VER[0], p))
		if not os.path.exists(zip_file):
			if not download_info:
				fh = urllib.urlopen(REL_LIST_URL)
				data = fh.read()
				fh.close()
				versions = json.loads(data)["releases"]
				download_info = [v for v in versions if v["version"] == SDK_VER[0]]
			# download the zip and put in DIR
			for info in download_info:
				if info["name"] == "mobilesdk" and info["os"] == p:
					url  = info["url"]
					print "Fetching %s zip for %s...\n" % (SDK_VER[0], p)
					urllib.urlretrieve(url, zip_file, download_status)
					sys.stdout.write("\n")
					break

def write_bom(zip_path, bom_path):
	z = zipfile.ZipFile(zip_path, "r")
	contents = sorted(set(z.namelist()))
	with open(bom_path, "w") as f:
		f.write("\n".join(contents))
	z.close()

def write_boms():
	for platform in (PLATFORMS):
		file_path = os.path.join(DIR, "mobilesdk-%s-%s.zip" % (SDK_VER[0], platform))
		write_bom(file_path, os.path.join(DIR, "mobilesdk-%s-%s.bom" % (SDK_VER[0], platform)))
		file_path = os.path.join(DIR, "mobilesdk-%s-%s.zip" % (SDK_VER[1], platform))
		write_bom(file_path, os.path.join(DIR, "mobilesdk-%s-%s.bom" % (SDK_VER[1], platform)))

def compare(platform):
	old_list_file = os.path.join(DIR, "mobilesdk-%s-%s.bom" % (SDK_VER[0], platform))
	new_list_file = os.path.join(DIR, "mobilesdk-%s-%s.bom" % (SDK_VER[1], platform))
	with open(old_list_file, "r") as f:
		old_lines = f.readlines()
	with open(new_list_file, "r") as f:
		new_lines = f.readlines()

	old_sdk_prefix = "mobilesdk/%s/%s" % (platform, SDK_VER[0])
	new_sdk_prefix = "mobilesdk/%s/%s" % (platform, SDK_VER[1])
	old_cloud_prefix = "modules/commonjs/ti.cloud/%s" % TI_CLOUD[0]
	new_cloud_prefix = "modules/commonjs/ti.cloud/%s" % TI_CLOUD[1]
	old_push_prefix = "modules/android/ti.cloudpush/%s" % TI_CLOUD_PUSH[0]
	new_push_prefix = "modules/android/ti.cloudpush/%s" % TI_CLOUD_PUSH[1]

	log_file = os.path.join(DIR, "%s-results.txt" % platform)
	if os.path.exists(log_file):
		os.remove(log_file)

	def log(s):
		with open(log_file, "a") as f:
			f.write("%s\n" % s)

	def check_diffs(left_side, right_side):
		if left_side == "old":
			left_sdk_ver = SDK_VER[0]
			right_sdk_ver = SDK_VER[1]
			left_lines = old_lines
			right_lines = new_lines
			left_sdk_prefix = old_sdk_prefix
			right_sdk_prefix = new_sdk_prefix
			left_cloud_prefix = old_cloud_prefix
			right_cloud_prefix = new_cloud_prefix
			left_push_prefix = old_push_prefix
			right_push_prefix = new_push_prefix
		else:
			left_sdk_ver = SDK_VER[1]
			right_sdk_ver = SDK_VER[0]
			left_lines = new_lines
			right_lines = old_lines
			left_sdk_prefix = new_sdk_prefix
			right_sdk_prefix = old_sdk_prefix
			left_cloud_prefix = new_cloud_prefix
			right_cloud_prefix = old_cloud_prefix
			left_push_prefix = new_push_prefix
			right_push_prefix = old_push_prefix

		for line in left_lines:
			if not line.strip().endswith("/"):
				if line.startswith(left_sdk_prefix):
					to_compare = line.replace(left_sdk_prefix, right_sdk_prefix)
				elif line.startswith(left_cloud_prefix):
					to_compare = line.replace(left_cloud_prefix, right_cloud_prefix)
				elif line.startswith(left_push_prefix):
					to_compare = line.replace(left_push_prefix, right_push_prefix)
				else:
					to_compare = line

				if to_compare not in right_lines:
					log("%s in %s but not %s" % (line.strip(), left_sdk_ver, right_sdk_ver))

	check_diffs("old", "new")
	check_diffs("new", "old")
	
if __name__ == "__main__":
	#get_old_zips()
	write_boms()

	for platform in PLATFORMS:
		compare(platform)


