#!/bin/python

import requests as rq
import os

class crawler():
  def __init_(self):
    self.proxies = {'http': 'socks5://localhost:9050','https': 'socks5://localhost:9050'}
    self.ahmia = "https://www.ahmia.fi/onions"
    self.file = open("list.txt","w+")
  def get_links():
    self.r =  rq.get(self.ahmia,proxies=self.proxies).text()
    self.file.write(self.file)
  def shoter(self):
    
    
