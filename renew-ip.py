from stem import Signal
from stem.control import Controller
import requests
session = requests.session()
# Tor uses the 9050 port as the default socks port
session.proxies = {'http':  'socks5://127.0.0.1:9050',
                   'https': 'socks5://127.0.0.1:9050'}

# Make a request through the Tor connection
# IP visible through Tor
print session.get("http://httpbin.org/ip").text

# signal TOR for a new connection 
def renew():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password="password")
        controller.signal(Signal.NEWNYM)
        print session.get("http://httpbin.org/ip").text
        
renew()
