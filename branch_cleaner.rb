#!/usr/bin/env ruby

require 'optparse'
require 'git'
require 'net/http'
require 'json'

options = {
	:verbose => false,
	:noop => false,
	:clean_remote => false,
	:whitelist => [],
	:dir => Dir.pwd,
	:jira_prefix => "TIMOB",
	:git_prefix => nil,
	:jira => 'https://jira.appcelerator.org',
	:remote => 'origin',
}

rest_path = 'rest/api/2.0.alpha1/issue/'
OptionParser.new do |opts|
	opts.banner = "Usage: #{$0} [options]"
	opts.on('-v', '--verbose', "Run verbosely") do |v|
		options[:verbose] = v
	end
	opts.on('-d', '--dir', "Clone directory") do |d|
		
	end
	opts.on('--dry-run', "Don't actually modify anything") do |d|
		options[:noop] = d
	end
	opts.on('-w', '--whitelist [NUMBER|FEATURE|ETC.]', 
			"'Whitelist' branches with these in their name so they are not purged.") do |ticket|
		options[:whitelist] << ticket
	end
	opts.on('-p', '--project NAME', String, 
			"JIRA project prefix for tickets") do |name|
		options[:jira_prefix] = name
	end
	opts.on('--branch-prefix', String, 
			"Prefix for branches (default: lowercase 'project')") do |prefix|
		options[:git_prefix] = prefix
	end
	opts.on('-r', '--remote NAME', String,
			"Name of the remote") do |r|
		options[:remote] = r
	end
	opts.on('--[no]-clean-remote', Boolean, 
			"Whether or not to also clean remotes (default false)") do |clean|
		options[:clean_remote] = clean
	end

	opts.on_tail('-h', '--help', 'Display help') do |h|
		puts opts
		exit
	end
end.parse!

repository = Git.open(options[:dir])
if (options[:git_prefix].nil?)
	options[:git_prefix] = options[:jira_prefix].downcase
end

url = options[:jira] << '/' << rest_path
repository.branches.local.each do |branch|
	if /^#{options[:git_prefix]}-(\d*)/ =~ branch.name
		ticket = $1
		skip = false
		puts "Processing #{branch.name}..."
		options[:whitelist].each do |name|
			if /#{name}/ =~ branch.name
				puts "\tSkipping (whitelisted #{name})" if options[:verbose]
				skip=true
				break
			end
		end
		next if skip
		
		uri = URI.parse("#{url}#{options[:jira_prefix]}-#{ticket}")
		client = Net::HTTP.new(uri.host, uri.port)
		client.use_ssl = true
		request = Net::HTTP::Get.new(uri.path)
		response = client.start {|http| http.request(request)}

		issue = JSON.parse(response.body)
		unless issue["errorMessages"].nil?
			puts "\tUnable to access ticket #{ticket}: #{issue["errorMessages"]}"
			next
		end
		resolution = issue["fields"]["status"]["value"]["name"]
		
		if /Resolved|Closed/ =~ resolution
			puts "\tTicket for #{branch.name} is resolved..." if options[:verbose]
			puts "\tRemoving local #{branch.name}..."
			branch.delete unless options[:noop]
			
			if options[:clean_remote]
				puts "\tRemoving remote #{options[:remote]}/#{branch.name}..."
				
				# git module doesn't appear to have support for remote branch
				# deletion, so we do it the ugly way
				`git push #{options[:remote]} :#{branch.name}` unless options[:noop]
			end
		end
	end
end