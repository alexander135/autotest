import urllib.request
import re
from bs4 import BeautifulSoup
a = urllib.request.urlopen("http://10.50.1.35:8080/ui/generic/stand?testuser=astsplus@fitfond@spt5&mode=list ")
soup = BeautifulSoup(a, "html.parser" )
data = {'job': {}}
info = soup.find_all("div",attrs = {"class" : "data-block"})[1].find_all("div")[0].find_all("div")[2:5]
for i in info:
	res = re.split(': ', i.get_text())
	data['job'][res[0]] = res[1]
print(info)
names = []
k = 0
for name in soup.find_all("h3")[6:14]:
	names.append(name.string)
name_index = 0
for table in soup.find_all("table")[1:9]:
	name = names[name_index]
	data[name] = {"WARNING" : 0, 'PASSED' : 0, 'FAILED' : 0, "ERROR" : 0}
	for tr in table.find_all("tr"):
		i  = tr.find_all("td")[2].find_all("div")[1]
		i.a.decompose()
		i.div.decompose()
		k+= 1
		status  = re.search("\w+", i.get_text()).group(0)
		data[name][status] += 1
	name_index += 1
print(k, data)
