#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests as rq
from bs4 import BeautifulSoup as bs
from stem import Signal
from stem.control import Controller
import time

def get_onions():
	link = "https://ahmia.fi/onions/"
	r = (rq.get(link)).content
	html = bs(r,"html.parser")
	onion = html.find("br").parent
	l = (onion.text).replace(" ","").replace("\n\n","\n")
	return l
def write_onions():
	onions = get_onions()
	print onions
	file = open("onions.txt","a+")
	file.write(onions)
	links = file.readlines()
	return links

def read_onions():
	lines = write_onions()
	proxies = {'http':  'socks5://127.0.0.1:9050','https': 'socks5://127.0.0.1:9050'}
	try:
		for line in lines:
			send_requests(line,proxies)

	except:
		print "error"


#read_onions()

def send_requests(onion,proxies):	
	try:
		r = rq.get(str(onion),proxies=proxies)
		html = bs(r.content,"html.parser")
		title = html.title.text
		print "[+] %s \t %s"%(title, onion)

	except:
		print "[-] Error"



def change():

# Tor uses the 9050 port as the default socks port
	proxies = {'http':  'socks5://127.0.0.1:9050','https': 'socks5://127.0.0.1:9050'}
	link = "http://ipinfo.io/json"
	r = rq.get(link,proxies=proxies)
	print r
	renew()
	r = rq.get(link,proxies=proxies)
	print r


# signal TOR for a new connection 
def renew():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password="5w0rdf15h")
        controller.signal(Signal.NEWNYM)
        time.sleep(5)
       
        
