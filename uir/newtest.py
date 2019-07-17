from bs4 import BeautifulSoup
import urllib.request
import json

mes = eval(urllib.request.urlopen("http://asts-jenkins.moex.com/job/rebus.autobus.tests/3935/api/python?pretty=true").read())

params = mes['actions'][0]['parameters'] 
dir = filter(lambda x: 'TDIR' == x['name'], params)
print(list(dir)[0]['value'])
