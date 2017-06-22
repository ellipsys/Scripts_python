#https://stackoverflow.com/questions/30286293/make-requests-using-python-over-tor
import requests
session = requests.session()
# Tor uses the 9050 port as the default socks port
session.proxies = {'http':  'socks5://127.0.0.1:9050',
                   'https': 'socks5://127.0.0.1:9050'}

# Make a request through the Tor connection
# IP visible through Tor
print session.get("http://httpbin.org/ip").text
# Above should print an IP different than your public IP

# Following prints your normal public IP
print requests.get("http://httpbin.org/ip").text
