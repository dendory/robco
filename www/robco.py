# RobCo Unified Operating System - (C) 2015 Patrick Lambert - http://dendory.net
# Not affiliated with Fallout or Bethesda
# Required to work: pip install psutil

import cgitb
import cgi
import json
import random
import re
import hashlib
import psutil

#
# Variables
#

output = {}
q = cgi.FieldStorage()


#
# Headers
#

print("HTTP/1.0 200 OK")
print("Content-Type: application/javascript; charset=utf-8")
print()


#
# Functions
#

# Only leave alphanumeric chars
def sanitize_alpha(text):
	return re.sub(r'[^A-Za-z0-9_\-\.]+', '', text)

# Produce random HEX addresses
def random_addresses(num):
	results = []
	for i in range(num):
		results.append(str(hex(random.randint(100000, 999999))))
	return results 

# Set output for normal elements
def set_output(expect, query, elements):
	global output
	output["expect"] = expect
	output["query"] = query
	output["elements"] = []
	for element in elements:
		output["elements"].append(element)

# Set output for an error
def set_err(err):
	global output
	output["expect"] = ""
	output["query"] = "input"
	output["elements"] = []
	output["elements"].append({"type": "text", "content": ["An internal server error occurred!<br>Error: " + str(err) + "<br><br>" + str(random_addresses(5)) + "<br>" + str(random_addresses(5)) + "<br>" + str(random_addresses(5))]})

# Print output and quit
def done():
	print(json.dumps(output, sort_keys=True, indent=4))
	quit()


#
# Main loop
#

# Open files
try:
	f = open("../datasets/files.json", "r")
	files = json.loads(f.read())
	f.close()
except Exception as err:
	set_err(err)
	done()

# Check for input variables
cmd = str(q.getvalue("cmd"))
expect = str(q.getvalue("expect"))
secret = str(q.getvalue("secret"))

try:
	words = cmd.split(' ')
	if len(words) > 0:
		if 'USERNAME' in expect:
			set_output("PASSWORD " + sanitize_alpha(words[0].upper()), "password", [{"type": "text", "content": "Enter password:"}])
		elif 'PASSWORD' in expect and len(expect.split(' ')) > 1:
			userlist = files["/DEBUG/ACCOUNTS.F"]["content"];
			found = 0
			for user in userlist.split('\n'):
				if str(expect.split(' ')[1]).upper() == user.split(':')[0]:
					found = 1
					if hashlib.sha1(cmd.encode('utf8')).hexdigest() == user.split(':')[1]:
						found = 2
						set_output("", "input", [{"type": "secret", "content": user.split(':')[1]}, {"type": "text", "content": "Welcome back, " + user.split(':')[0]}, {"type": "username", "content": str(expect.split(' ')[1])}])
			if found == 1:
				set_output("", "input", [{"type": "disconnect", "content": "Bad username or password."}])
			elif found == 0:
				set_output("CREATEUSER " + str(expect.split(' ')[1]).upper() + " " + hashlib.sha1(cmd.encode('utf8')).hexdigest(), "password", [{"type": "text", "content": "Username " + str(expect.split(' ')[1]).upper() + " does not exist in current dataset. Adding user...<br><br>Please retype password:"}])
		elif 'CREATEUSER' in expect and len(expect.split(' ')) > 2:
			if hashlib.sha1(cmd.encode('utf8')).hexdigest() != str(expect.split(' ')[2]):
				set_output("", "input", [{"type": "disconnect", "content": "Passwords do not match."}])
			else:
				files["/DEBUG/ACCOUNTS.F"]["content"] += "\n" + str(expect.split(' ')[1]) + ":" + str(expect.split(' ')[2])
				f = open("../datasets/files.json", "w")
				f.write(json.dumps(files, sort_keys=True, indent=4))
				f.close()
				set_output("", "input", [{"type": "text", "content": "User " + str(expect.split(' ')[1]) + " added to dataset.<br>Saving to DEBUG/ACCOUNTS.F"}, {"type": "username", "content": str(expect.split(' ')[1])}])	
		elif ('CON' == words[0].upper() or 'CONNECT' == words[0].upper()) and secret == "None":
			servernum = str(random.randint(1, 9))
			if len(words) > 1:
				set_output("PASSWORD " + sanitize_alpha(words[1].upper()), "password", [{"type": "server", "content": "Server " + servernum}, {"type": "text", "content": "Connected to Server " + servernum + "...<br><br>Initializing RobCo Industries(TM) MF Boot Agent v2.1.0352<br>RETROS BIOS - Freemem: " + str(int(psutil.virtual_memory()[4]/1000)) + " KB - Usedmem: " + str(int(psutil.virtual_memory()[3]/1000)) + " KB - Datasets: " + str(len(files)) + "<br> Normal mode<br>Ready."}, {"type": "text", "content": "Enter password:"}])
			else:
				set_output("USERNAME", "input", [{"type": "server", "content": "Server " + servernum}, {"type": "text", "content": "Connected to Server " + servernum + "...<br><br>Initializing RobCo Industries(TM) MF Boot Agent v2.8.0352<br>RETROS BIOS - Freemem: " + str(int(psutil.virtual_memory()[4]/1000)) + " KB - Usedmem: " + str(int(psutil.virtual_memory()[3]/1000)) + " KB - Datasets: " + str(len(files)) + "<br>Normal mode<br>Ready."}, {"type": "text", "content": "Enter username:"}])
		elif 'COUNT' == words[0].upper() or 'CALC' == words[0].upper():
			if len(words) == 4:
				if words[2] == '+':
					set_output("", "input", [{"type": "text", "content": str(int(words[1]) + int(words[3]))}])
				elif words[2] == '-':
					set_output("", "input", [{"type": "text", "content": str(int(words[1]) - int(words[3]))}])
				elif words[2] == '*':
					set_output("", "input", [{"type": "text", "content": str(int(words[1]) * int(words[3]))}])
				elif words[2] == '/':
					set_output("", "input", [{"type": "text", "content": str(int(words[1]) / int(words[3]))}])
				else:
					set_err("Invalid operant for COUNT.")
			else:
				set_err("Invalid number of arguments for COUNT.")
		elif 'CLS' == words[0].upper() or 'CLEAR' == words[0].upper():
			set_output("", "input", [{"type": "cls", "content": ""}])
		elif 'SNAKE' == words[0].upper():
			set_output("", "input", [{"type": "snake", "content": "<div id='s' tabindex='0'></div>"}])
		elif 'DIR' == words[0].upper() or 'DIRECTORY' == words[0].upper():
			folder = ""
			if len(words) > 1:
				folder = sanitize_alpha(words[1]).upper()
			results = "Datasets for: " + folder + "/*<br><table><tr><th>NAME</th><th>OWNER</th><th>PERMS</th><th>SIZE</th></tr>";
			for k in files.keys():
				if folder == k.split('/')[1] or folder == "":
					results += "<tr><td>" + k + "</td><td>" +  files[k]['owner'] + "</td><td>" + files[k]['perms'] + "</td><td>" + str(len(files[k]['content'])) + "</td></tr>";
			set_output("", "input", [{"type": "text", "content": results}])
		elif 'HELP' == words[0].upper():
			if len(words) == 1:
				set_output("", "input", [{"type": "text", "content": "RobCo Interactive Help System.<br><br>To get help on a specific command, type: <b>HELP [command]</b><br>Available commands: <b>HELP</b>, <b>DISCONNECT</b>, <b>DIRECTORY</b>, <b>CLEAR</b>, <b>COUNT</b>"}])
			else:
				if 'HELP' in words[1].upper():
					set_output("", "input", [{"type": "text", "content": "<b>HELP [command]:</b> Obtain contextual help on specific commands."}])
				elif 'DISCONNECT' in words[1].upper():
					set_output("", "input", [{"type": "text", "content": "<b>DISCONNECT:</b> Disconnects your terminal from the server."}])
				elif 'COUNT' in words[1].upper():
					set_output("", "input", [{"type": "text", "content": "<b>COUNT [number] [operant] [number]:</b> Count numbers."}])
				elif 'CLEAR' in words[1].upper():
					set_output("", "input", [{"type": "text", "content": "<b>CLEAR:</b> Clears the terminal output."}])
				elif 'DIRECTORY' in words[1].upper():
					set_output("", "input", [{"type": "text", "content": "<b>DIRECTORY [directory]:</b> Lists all datasets from the root directory or a specific one."}])
				else:
					set_output("", "input", [{"type": "text", "content": "Unknown command."}])
		else:
			set_output("", "input", [{"type": "text", "content": "Invalid command! Try <b>HELP</b>."}])
except Exception as err:
	set_err(err)
	done()
# Finished processing
done()
