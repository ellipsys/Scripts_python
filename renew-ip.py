import requests as rq
import time
from stem import Signal
from stem.control import Controller
import os

def renew_tor_ip():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password="5w0rdf15h")
        controller.signal(Signal.NEWNYM)
	print "waiting...!"
	time.sleep(4)

proxies = {
        "https":"socks5://127.0.0.1:9050",
        "http":"socks5://127.0.0.1:9050"
}
while True:
	try:
		renew_tor_ip()
		r = (rq.get("http://icanhazip.com/", proxies=proxies).content).replace("\n","")
		r =rq.get("http://ip-api.com/json/%s"%r,proxies=proxies).content
		print r
		time.sleep(300)
	except:
		os.system("sudo service tor start")
		pass
