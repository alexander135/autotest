import urllib.request
from bs4 import BeautifulSoup
import pymongo
import os
import yaml
page = urllib.request.urlopen("http://10.50.170.25/ui/lastrun?testuser=fitrebus6")
soup = BeautifulSoup(page, "html.parser")


data_block = soup.find_all("div", attrs = {"class" : "page-block"})[1].find("div", attrs = {"class" : "data-block"}).find("div").find_all("div")

data = {"job":{}, "res" : {}, "problems" : []}

for i in range(4):
    key, value = str(data_block[i].string).split(": ")
    data['job'][key] = value


for i in range(4, 11):
    key, value = str(data_block[i].string).split(": ")
    data['res'][key]= value
if data['res']['Total'] != data['res']['Pass']:
    table = soup.find("table").find_all("tr")
    for row in table:
        for i in row.stripped_strings:
            data['problems'].append(i)



config = yaml.load(open('config.yaml'))
print(type(config['FI_curr_RHEL6']['fitrebus6']['id']))
conn = pymongo.MongoClient(username = os.environ['mongo_login'], password = os.environ['mongo_password'], host = config['db']['host'], port = config['db']['port'])
print(problems = conn.testresults["firebus6"].find_one({"job.pk": config['FI_curr_RHEL6']["fitrebus6"]['id']})['problems']
)
