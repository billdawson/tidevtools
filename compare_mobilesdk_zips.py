#!/usr/bin/env python
import zipfile, os, sys

DIR = "/Users/bill/tmp"
PLATFORMS = ("osx", "win32", "linux")
TI_CLOUD = ("2.0.1", "2.0.4") # old versus new
TI_CLOUD_PUSH = ("2.0.1", "2.0.3")
SDK_VER = ("2.0.1.GA2", "2.0.2")

def write_bom(path, platform, label):
	z = zipfile.ZipFile(path, "r")
	contents = sorted(set(z.namelist()))
	out_path = os.path.join(DIR, "%s-%s.txt" % (platform, label))
	with open(out_path, "w") as f:
		f.write("\n".join(contents))
	z.close()

def write_boms():
	for platform in (PLATFORMS):
		file_path = os.path.join(DIR, "mobilesdk-%s-%s.zip" % (SDK_VER[0], platform))
		write_bom(file_path, platform, "old")
		file_path = os.path.join(DIR, "mobilesdk-%s-%s.zip" % (SDK_VER[1], platform))
		write_bom(file_path, platform, "new")

def compare(platform):
	old_list_file = os.path.join(DIR, "%s-old.txt" % platform)
	new_list_file = os.path.join(DIR, "%s-new.txt" % platform)
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

	log_file = "%s-results.txt" % platform
	if os.path.exists(log_file):
		print "heck"
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
	
write_boms()

for platform in PLATFORMS:
	compare(platform)


