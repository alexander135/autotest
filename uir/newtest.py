from bs4 import BeautifulSoup
import urllib.request
import json

mes = urllib.request.urlopen("http://10.50.1.35:8080/ui/standsstatus").read()
data = json.loads(mes)
for item in data:
	if item['stand'] == "astsplus@fitfond@spt5":
		if item['status']:
			print('Stand in use')
		else:
			print('stand free')
print(data)
