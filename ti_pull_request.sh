#!/bin/bash
#
# Pre-fills common values in a github pull request
# for titanium_mobile w/ JIRA
#
# To be useful, this script makes a lot of assumptions:
# 1) You are logged in to github
# 2) You have Google Chrome, and OSX
# 3) You have a version of Python with the "json" module installed
# 4) Your pull request branch is named like "timob-XXXX"
# 5) Your personal fork's remote name is "origin"
# 6) Your branch is pushed

jira_rest_url="http://jira.appcelerator.org/rest/api/2.0.alpha1/issue"
summary_py=$(cat <<CODE
import sys, json
try:
	issue = json.load(sys.stdin);
	sys.stdout.write(issue["fields"]["summary"]["value"])
except Exception, e:
	sys.stdout.write("__ERROR__:" + e)
CODE)

branch_name=$(git status -b -s | grep '##' | sed 's/## //')
timob_issue=$(echo $branch_name | tr '[:lower:]' '[:upper:]')

if [[ $timob_issue != TIMOB-* ]]; then
	echo "Error: Branch names must follow the form timob-XXXX"
	exit 1
fi

echo "Getting $jira_rest_url/$timob_issue"
issue_summary=$(curl -s "$jira_rest_url/$timob_issue" | python -c "$summary_py" | sed 's/"/\\"/g')

if [[ $issue_summary == __ERROR__* ]]; then
	echo "Error: Couldn't load issue summary from JIRA"
	exit 1
fi

issue_url="http://jira.appcelerator.org/browse/$timob_issue"
github_project=$(git config remote.origin.url | sed 's/git@github.com://' | sed 's/\.git//')
pull_request_url="https://github.com/$github_project/pull/new/$branch_name"

applescript=$(cat <<SCRIPT
tell application "Google Chrome"
	activate
	tell window 1
		set newTab to make new tab with properties {URL:"$pull_request_url"}
		delay 1
		tell active tab
			-- wait for page to load
			repeat
				set isLoading to loading
				if isLoading = false then exit repeat
				delay 0.1
			end repeat
			-- finished loading, run our JS
			execute javascript "document.getElementById('pull_body').value = '$issue_url'; document.getElementsByClassName('title')[0].value = '$timob_issue: $issue_summary';"
		end tell
	end tell
end tell
SCRIPT)

/usr/bin/osascript -e "$applescript"
