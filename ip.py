import requests
import json

a="181.54.153."
c = open("eli.txt","w")
def ip_search():
	for i in range(0,255):
		i=i+1
		b=a+str(i)
		r=requests.get("http://ipinfo.io/"+b+"/json")
		h=r.json()
		p=str(r.status_code)
		if p=="200":
                        c.write(b+"\n");
                        c.write(str(h)+"\n"+"\n");
                        print "En proceso "+b
		
		
ip_search()

print "listo"
