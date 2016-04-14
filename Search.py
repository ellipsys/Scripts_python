
#! /usr/bin/env python
# coding=UTF-8
# Crawler_Shodan


import time
from shodan import WebAPI

SHODAN_API_KEY = "Ingrese la API KEY SHODAN"

# Crear coneccion con API SHODAN
api = WebAPI(SHODAN_API_KEY)


def query_Shodan(term, callback):
	templist = []
	try:
		i=1
		while True:
			#Busqueda Shodan
			results = api.search(term,page=i)

			#Construir diccionario con los resultados
			for result in results['matches']:
				temp = {}
				temp["Query"] = term 
				host = api.host('%s' %result['ip'])
				ip = '%s' %result['ip']
				temp["IP"] = ip.encode('ascii', 'replace')
				hostnames = s = ''.join(host.get('hostnames', None))
				temp["Hostnames"] = hostnames.encode('ascii', 'replace')
				os = '%s' %host.get('os', None)			
				temp["OS"] = os.encode('ascii', 'replace')
				port = '%s' %host.get('port', None)			
				temp["Port"] = port.encode('ascii', 'replace')
				banner = '%s' %host.get('banner', None)
				temp["Banner"] = banner.encode('ascii', 'replace')
				ccode = '%s' %host.get('country_code', None)
				temp["Country Code"] = ccode.encode('ascii', 'replace')
				cname = '%s' %host.get('country_name', None)
				temp["Country Name"] = cname.encode('ascii', 'replace')
				city = '%s' %host.get('city', None)				
				temp["City"] = city.encode('ascii', 'replace')
				longitude = '%s' %host.get('longitude', None)
				temp["Longitude"] = longitude.encode('ascii', 'replace')
				latitude = '%s' %host.get('latitude', None)
				temp["Latitude"] = latitude.encode('ascii', 'replace')
				timestamp = '%s' %host.get('timestamp', None)
				temp["Timestamp"] = timestamp.encode('ascii', 'replace')
				updated = '%s' %result['updated']
				temp["Updated"] = updated.encode('ascii', 'replace')
				data = '%s' %result['data']				
				temp["Data"] = data.encode('ascii', 'replace')
				templist.append(temp)
				callback(temp)
			i += 1
	except Exception, e:
		#No results found, print no 'matches'
		print 'No %s\r' %e
	#Returns a list of dictionary objects. Each dictionary is a result
	return templist


def print_result(info):
	print info

#Ejemplo
list = query_Shodan('net:87.239.102.7', print_result)

#Ejemplo 2
for match in list:
	for field in match:
		print field
		print match[field]
		print ''
	print '-------------------'
