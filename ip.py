import requests as rq
import json


def main():
	r=rq.get("http://ipinfo.io/"+b+"/json")
	content=r.json()
	code=str(r.status_code)
	if p=="200":
        	print "[+] You stay conected\n%s",%(content)
		
		
if __name__=="__main__":
	main()

