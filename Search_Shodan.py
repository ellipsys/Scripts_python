#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
from shodan import WebAPI

# SHODAN API Key
SHODAN_API_KEY = "GM5SvHv2uHxEjSN0NlA7ZJl77SI2Ob7y"
api = WebAPI(SHODAN_API_KEY)


# Argumentos##################################################
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--shodan", help="Use the SHODAN API to search.", nargs='*')
#parser.add_argument("-s", "--shodan-host", help="Use the SHODAN API to search by specific host name.", nargs='*')
parser.add_argument("-e", "--exploit", help="Search and download from Exploit DB", nargs='*')
parser.add_argument("-w", "--whois", help="Run a WHOIS search by IP or Domain", nargs='*')
parser.add_argument("-n", "--nslookup", help="Perform DNS queries", nargs='*')
parser.add_argument("-o", help="Specify an output file to write the results to", nargs='*')
args = parser.parse_args()
###################################################################

def main():
		
	return 0

#Basic SHODAN Search Query.	
def shodan_basic_search():
	shodan_query= ' '.join(args.shodan)
	
	# Wrap the request in a try/ except block to catch errors
	try:
		# Search Shodan
		results = api.search(shodan_query)

		# Show the results
		print 'Results found: %s' % results['total']
		raw_input()
		for result in results['matches']:
			print 'IP: %s' % result['ip']
			print result['data']
			print ''
	except Exception, e:
		print 'Error: %s' % e

def shodan_menu():
	print('\nSHODAN Menu Options\n')
	print('1 - Lists all hosts found')
	print('2 - Narrow down the search results by country')
	print('3 - Write results list to a file in the CWD')
	print('4 - Run a new SHODAN search')
	print('5 - Exit')
	global selection_shodan
	selection_shodan = raw_input('\nSelect an option from above: ')

#SHODAN Search 2
def shodan():
	search_query = ' '.join(args.shodan)
	results = api.search(search_query)
	
	if len(results) > 0:
		print("Searching................\n")
		print("Search Executed Successfully")
		print("There are %s hosts found that relate to %s" % (results['total'],search_query))
		print("See Menu below for options")
		
	shodan_menu()
	
	while True:

		if selection_shodan == '1':
			print('\nHost IP Hostname\n')
			for host in results['matches']:
				print('%s:%s %s %s' % (host['ip'],host['port'],host['os'],host['hostnames'])
        elif selection_shodan == '2':
			country_code = raw_input('Enter the country code to search: ')
			print('\nShowing results with %s country code\n' % country_code)
			for host in results['matches']:
				if country_code == host['country']:
					print('%s:%s %s %s' % (host['ip'],host['port'],host['os'],host['hostnames'])

		elif selection_shodan == '3':
			for host in results['matches']:
				output = open('shodan_results.txt', 'w')
				output.write('Country: ', results['country'])
				output.write('Hostname: ', results['hostnames'])
				output.write('IP Address: ', results['ip'])
				output.write('Port: ', results['port'])
				output.write('OS: ', results['os'])
				output.write('Data: ', results['data'])
				output.write('Date updated: ', results['updated'])
				output.close()

		elif selection_shodan == '4':
			new_search = raw_input('Enter new SHODAN search: ')
			results = api.search(new_search)
			print("Searching................\n")
			print("Search Executed Successfully")
			print("There are %s hosts found that relate to %s" % (results['total'],new_search))
			print("See Menu below for options")

		elif selection_shodan == '5':
			print('Happy Hacking!')
			sys.exit(0)

		shodan_menu()

#ExploitDB Search
def exploitdb():
	# initial exploit-db search search
	search_query = ' '.join(args.exploit)
	results = api.exploitdb.search(search_query)

	if len(results) > 0:
		print("Searching................\n")
		print("Search Executed Successfully")
		print("There are %s Exploits Found that relate to %s" % (results['total'],search_query))
		print("See Menu below for options")

	exploit_menu()
	# menu options end

	# if statements
	while True:

		if selection == '1':
			print('\nexploit id: description\n')
			for exploit in results['matches']:
				print('%s: %s' % (exploit['id'],exploit['description']))

		if selection == '2':
			print('exploit types : remote, webapps, dos, local, shellcode')
			exploit_type = raw_input('enter the type of exploit: ')
			print('\ndisplaying %s exploits\n' % exploit_type)
			for exploit in results['matches']:
				if exploit_type == exploit['type']:
					print('%s: %s' % (exploit['id'],exploit['description']))

		if selection == '3':
			exploit_id = raw_input('\nenter the exploit id to be displayed: ')
			for exploit in results['matches']:
				if exploit_id == str(exploit['id']):
					exploit_file = api.exploitdb.download(exploit['id'])
					print 'Filename: %s' % exploit_file['filename']
					print 'Content-type: %s' % exploit_file['content-type']
					print exploit_file['data']

		if selection == '4':
			exploit_id = raw_input('\nenter exploit id: ')
			for exploit in results['matches']:
				if exploit_id == str(exploit['id']):
					exploit_dl = api.exploitdb.download(exploit['id'])
					output = open(exploit_dl['filename'], 'w')
					output.write(exploit_dl['data'])
					output.close()

		if selection == '5':
			new_search = raw_input('enter new search string: ')
			results = api.exploitdb.search(new_search)
			print("Searching................\n")
			print("Search Executed Successfully")
			print("There are %s Exploits Found that relate to %s" % (results['total'],new_search))
			print("See Menu below for options")

		if selection == '6':
			print('Happy Hacking!')
			sys.exit(0)

		exploit_menu()
	

# Exploit DB menu options
def exploit_menu():
	print('\nMenu Options\n')
	print('1 - list all exploits found')
	print('2 - select the type of exploits to display')
	print('3 - select a exploit to view')
	print('4 - write exploit to a file in the CWD')
	print('5 - change search string')
	print('6 - exit')
	global selection
	selection = raw_input('\nSelect an option from above: ')

#Basic WHOIS Query		
def whois():
	print "WHOIS Lookup"


#NSLOOKUP Options
def nslookup():
	print "NSLOOKUP"

#test to check arg values before running queries	
print args 

raw_input()
###################################

#Actual Program If/Else code#############################
if args.shodan:
	print "SHODAN Search Query: ", ' '.join(args.shodan)
	shodan()
elif args.exploit:
	exploitdb()
elif args.whois:
	print args.whois
	whois()
elif args.nslookup:
	print args.nslookup
	nslookup()

################################	
if __name__ == '__main__':
	main()
