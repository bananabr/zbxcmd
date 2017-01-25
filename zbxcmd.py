#!/usr/bin/env python
#coding:utf8

import optparse
import sys
import traceback
from getpass import getpass
from pyzabbix import ZabbixAPI
import json


command_args={}
filters={}

def add_cmd_arg(option, opt, value, parser):
	command_args[opt.lstrip('-')]=value

def add_filters(option, opt, value, parser):
	_key=value.split(":")[0]
	_value=value.split(":")[1]
	filters[_key]=_value
	
def get_options():
	commands={
		'host': host_cmd_parse,
		'hostgroup': hostgroup_cmd_parse,
		'trigger': trigger_cmd_parse,
		'itemprototype': item_proto_cmd_parse
	}
	
	valid_methods=['get']
	
	filters = {}
	
	usage = "usage: %prog [command][options]"
	OptionParser = optparse.OptionParser
	parser = OptionParser(usage)

	parser.add_option("-s","--server",action="store",type="string",\
		dest="server",help="(REQUIRED)Zabbix Server URL. Ex.: http://server.local/zabbix")
	
	parser.add_option("-u", "--username", action="store", type="string",\
		dest="username",help="(REQUIRED)Username (Will prompt if not given).")

	parser.add_option("-p", "--password", action="store", type="string",\
		dest="password",help="(REQUIRED)Password (Will prompt if not given).")

	parser.add_option("-U", "--http-user", action="store", type="string",\
		dest="http_username",help="Username for HTTP basic authentication.")

	parser.add_option("-P","--http-pass",action="store",type="string",\
		dest="http_password",help="Password for HTTP basic authentication (Will prompt if not given).")

	parser.add_option("-t","--timeout",action="store",type="int",default=3,\
		dest="timeout",help="Set connection timeout in seconds")

	parser.add_option("-c","--cmd",action="store",type="string",\
		dest="command", help="(REQUIRED)command. Available commands are: hostgroup,host,itemprototype,trigger")

	parser.add_option("-F", "--filter", action="callback", callback=add_filters, \
		type="string", help="filter key value pair")

	parser.add_option("-f","--fields",action="store",type="string",\
		dest="output", help="Comma separated list of fields to be retrieved ")

	parser.add_option("","--method",action="callback", callback=add_cmd_arg, \
		type="string", help="(REQUIRED)Command method to run")
	
	parser.add_option("","--include-triggers",action="store_true", \
		dest="include_triggers", help="Include triggers as child objects when available.")

	parser.add_option("","--include-hosts",action="store_true", \
		dest="include_hosts", help="Include hosts as child objects when available.")

	parser.add_option("","--depends-on",action="callback", callback=add_cmd_arg, \
		type="int", help="id of the object that it depends on.")

	options,args = parser.parse_args()

	if not options.command:
		errmsg("--cmd is a required argument!")

	if options.command not in commands:
		errmsg(options.command + " is not a valid command!")
	
	if 'method' not in command_args:
		errmsg("--method is a required argument!")

	if options.include_triggers:
		command_args["include-triggers"] = True

	if options.include_hosts:
		command_args["include-hosts"] = True

	if options.output:
		command_args["output"] = options.output

	if not options.server:
		options.server = raw_input('server http:')

	if not options.username:
		options.username = raw_input('Username:')

	if not options.password:
		options.password = getpass()

	if options.http_username and not options.http_password:
		options.http_password = getpass()

	options.command=commands[options.command]
	return options, args

def errmsg(msg):
	sys.stderr.write(msg + "\n")
	sys.exit(-1)

def validate_cmd_method(cmd,m,methods):
	if m not in methods:
		errmsg(m + " is not a valid method for the " + cmd + " command!")
		
def build_filter(command, args):
	result={}

	host_allowed_filters=['host']
	hostgroup_allowed_filters=['name']
	trigger_allowed_filters=['host','triggerid','priority']
	item_proto_allowed_filters=['hostid','name','type']

	command_allowed_filters={
		'host': host_allowed_filters,
		'trigger': trigger_allowed_filters,
		'hostgroup': hostgroup_allowed_filters,
		'item_proto': item_proto_allowed_filters
	}

	allowed_filters = command_allowed_filters[command]
	for f in allowed_filters:
		if (f in filters):
			result[f]=filters[f]

	return result	

def host_get(zapi,args):
	f=build_filter('host', args)
	options={}
	options['filter']=f

	if 'exclude-search' in args and args["exclude-search"]:
		options['excludeSearch'] = 1
	if 'include-triggers' in args and args['include-triggers']:
		options['selectTriggers']=["description","triggerid"]
	if 'output' in args:
		options['output']=args['output'].split(',')
	else:
		options['output']="extend"

	return zapi.host.get(**options)

def hostgroup_get(zapi,args):
	f=build_filter('hostgroup', args)
	options={}
	options['filter']=f

	if 'exclude-search' in args and args["exclude-search"]:
		options['excludeSearch'] = 1
	if 'include-hosts' in args and args['include-hosts']:
		options['selectHosts']=["hostid","name"]
	if 'output' in args:
		options['output']=args['output'].split(',')
	else:
		options['output']="extend"

	return zapi.hostgroup.get(**options)

def trigger_get(zapi,args):
	f=build_filter('trigger', args)
	options={}
	options['filter']=f

	if 'exclude-search' in args and args["exclude-search"]:
		options['excludeSearch'] = 1
	if 'output' in args:
		options['output']=args['output'].split(',')
	else:
		options['output']="extend"

	return zapi.trigger.get(**options)

def trigger_add_dependency(zapi,args):
	if 'triggerid' not in args:
		errmsg("You need to specify a triggerid to create a dependency.")
	if 'depends-on' not in args:
		errmsg("You need to specify the trigger-id the trigger depends on.")

	return zapi.trigger.adddependencies(triggerid=args['triggerid'], dependsOnTriggerid=args['depends-on'])

def item_proto_get(zapi,args):
	f=build_filter('item_proto', args)
	options={}
	options['filter']=f

	if 'exclude-search' in args and args["exclude-search"]:
		options['excludeSearch'] = 1
	if 'include-triggers' in args and args['include-triggers']:
		options['selectTriggers']=["description","triggerid"]
	if 'output' in args:
		options['output']=args['output'].split(',')
	else:
		options['output']="extend"

	return zapi.itemprototype.get(**options)

def trigger_cmd_parse(zapi,args):
	methods={
		'get': trigger_get,
		'adddependencies': trigger_add_dependency
	}
	validate_cmd_method('trigger',args['method'],methods)
	method=methods[args['method']]
	return method(zapi,args)

def hostgroup_cmd_parse(zapi,args):
	methods={
		'get': hostgroup_get
	}
	validate_cmd_method('hostgroup',args['method'],methods)
	method=methods[args['method']]
	return method(zapi,args)

def host_cmd_parse(zapi,args):
	methods={
		'get': host_get
	}
	validate_cmd_method('host',args['method'],methods)
	method=methods[args['method']]
	return method(zapi,args)

def item_proto_cmd_parse(zapi,args):
	methods={
		'get': item_proto_get
	}
	validate_cmd_method('itemprototype',args['method'],methods)
	method=methods[args['method']]
	return method(zapi,args)
	
if __name__ == "__main__":
	options, args = get_options()

	zapi = ZabbixAPI(options.server)

	# Enable HTTP auth
	if options.http_username and options.http_password:
		zapi.session.auth = (options.http_username, options.http_password)

	# Specify a timeout (in seconds)
	zapi.timeout = options.timeout
	zapi.login(options.username, options.password)

	qry_res = options.command(zapi, command_args)
	for i in qry_res:
		json.dump(i, sys.stdout, sort_keys=True, indent=4, separators=(',', ': '))
		sys.stdout.write('\n')