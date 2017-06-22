#!/usr/bin/python
import socks
import socket
import time
from stem.control import Controller
from stem import Signal
import urllib2
import sys

def info():
print "[*] Welcome to Chart-Cheat Script"
print "[*] This script works with running TOR only"
print "[*] usage is chartcheat.py domain"
print "[*] argument domain must be in format www.example.com"
print "[*] Example: chartcheat.py www.example.com"
return
if len(sys.argv)==2:
info();
counter = 0
url = str(sys.argv[1]);
with Controller.from_port(port = 9051) as controller:
    controller.authenticate()
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket
    #visiting url in infinite loop      
    while True:
        urllib2.urlopen("http://"+url)
        counter=counter+1
        print "Page " + url + " visited = " + str(counter)
        #wait till next identity will be available
        controller.signal(Signal.NEWNYM)
        time.sleep(controller.get_newnym_wait())            
else:
info();
