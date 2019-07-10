import urllib.request
import re
import json
import yaml
import pymongo
from datetime import datetime
import os
import logging
import logging.config
from bs4 import BeautifulSoup


os.chdir(os.path.dirname(os.path.abspath(__file__)))


config = yaml.load(open('config.yaml'))
logger_conf = yaml.load(open('logger_conf.yaml'))
logger_dict = logger_conf['logger_config']
logging.config.dictConfig(logger_dict)
logger = logging.getLogger('server.updating_script')
db_logger = logging.getLogger('server.updating_script.bd')



password_mgr = urllib.request.HTTPPasswordMgrWithPriorAuth()
top_level_url = "http://asts-jenkins.moex.com/"
password_mgr.add_password(None, top_level_url, config['user']['username'], config['user']['password'], is_authenticated = True)
handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
opener = urllib.request.build_opener(handler)
urllib.request.install_opener(opener)


def update(conn, flag = False):

    with open('lock.txt', 'w') as f:
        f.write('locked')
    res = {}
    result = {}
    logger.info('updating script started')
    config = yaml.load(open('config.yaml'))
    config['last_update'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(config['last_update'])
    with open('config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    for curname in config['jobs'].keys():
        curpath = config['PATH'] + curname + '/lastCompletedBuild/api/python?pretty=true'
        cur = eval(urllib.request.urlopen(curpath).read())
        if not conn.testresults[curname].count() or (int(cur['id']) != (config['jobs'][curname]['id'])):     
                        path = config['PATH'] + curname + '/' + cur['id'] + '/testReport/api/python?pretty=true'
                        res = {"job":{'name': curname,'id':int(cur['id']), 'date': datetime.fromtimestamp(cur['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')}}
                        try:
                            urllib.request.urlopen(path)
                        except:
                            logger.critical(path + ' error ')
                            result[curname] = 'Done'
                            pk = mongoSave(res,curname,conn)
                            
                            config['jobs'][curname]['id'] = int(cur['id'])
                            config['jobs'][curname]['pk'] = pk
                        
                        
                            with open('config.yaml', 'w') as f:
                                yaml.dump(config, f, default_flow_style=False)
                            continue 

                        logger.info('some new results were found')

                        try:
                            for subbuild in cur['subBuilds']:
                                if subbuild['result']:
                                    path = top_level_url + subbuild['url'] + 'testReport/api/python?pretty=true'
                                else:
                                    continue
                                
                                try:
                                    urllib.request.urlopen(path)  
                                except:
                                    continue

                                obj = eval(urllib.request.urlopen(path).read())
                                count_res(obj, res)
                        except:
                            obj = eval(urllib.request.urlopen(path).read())
                            count_res(obj, res)

                                                                    
                        soup = BeautifulSoup(urllib.request.urlopen(config['PATH'] + curname + '/' + cur['id'] + '/parameters/'), "html.parser")
                        names = soup.select('.setting-name')
                        name_list = []
                        value_list = []
                        for name in names:
                            name_list.append(name.string)
                        for tag in soup("input"):
                            if tag.has_attr("value"):
                                value_list.append(tag["value"])
                        parameters = dict(zip(name_list, value_list))
                        res["job"]["parameters"] = parameters 

                        pk = mongoSave(res,curname,conn)

                        config['jobs'][curname]['id'] = int(cur['id'])
                        config['jobs'][curname]['pk'] = pk
                        
                        
                        with open('config.yaml', 'w') as f:
                            yaml.dump(config, f, default_flow_style=False)

                        logger.info('test results have been updated')
                        result[curname] = 'Done'
        else:
                        logger.info(curname + ' already up to date')
                        result[curname] = 0
    if flag:
        for name in config['stand'].keys():
            res = update_stand(config['stand'][name]['id'])
            if res:
                pk = mongoSave(res, name, conn)
                result[name] = 'Done'
                config['stand'][name]['id'] = res['job']['Последний тест на данном стенде']
                config['stand'][name]['pk'] = pk
                with open('config.yaml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
            else:
                result[name] = 0
                logger.info(name + "already up to date")

    os.remove("lock.txt")
    return result 
 

def mongoSave(result, jobname, conn):
    db_logger.info('saving to db')
    db = conn.testresults
    db_logger.info('established connection to db')
    coll = db[jobname]
    result['job']['pk'] = coll.find().count() + 1
    coll.insert_one(result)
    db_logger.info('saved to db')
    return result['job']['pk']
    
    
def update_one(jobname, pk, conn):    
    config = yaml.load(open('config.yaml'))
    res = conn.testresults[jobname].find_one({"job.pk": int(pk)})
    logger.info(res)
    path = config['PATH'] + jobname + '/' + str(res['job']['id']) + '/testReport/api/python?pretty=true'
    try:
        urllib.request.urlopen(path)
    except:
        logger.critical(path + ' error ')
        return False
    soup = BeautifulSoup(urllib.request.urlopen(config['PATH'] + jobname + '/' + str(res['job']['id']) + '/parameters/'), "html.parser")
    names = soup.select('.setting-name')
    name_list = []
    value_list = []
    for name in names:
        name_list.append(name.string)
    for tag in soup("input"):
        if tag.has_attr("value"):
            value_list.append(tag["value"])
    parameters = dict(zip(name_list, value_list))
    res["job"]["parameters"] = parameters 
    result = conn.testresults[jobname].replace_one({"job.pk": int(pk)}, res)
    return result.modified_count
     

def count_res(obj, res):
    if 'suites' in obj.keys():
        for i in obj['suites'][0]['cases']:
            name = re.findall(r'\..+\.', i['className'])[0].split('.')[1]
            if name not in res.keys():
                res[name] = {'passed':0, 'failed':0, 'skipped':0, 'total':0}
            res[name]['total'] += 1
            if i['skipped'] == False:
                if (i['status'] != 'FAILED') and (i['status'] != 'REGRESSION'):
                    res[name]['passed'] += 1
                else:
                    res[name]['failed'] += 1
            else:
                res[name]['skipped'] += 1

def update_stand(cur_id):
    a = urllib.request.urlopen("http://10.50.1.35:8080/ui/generic/stand?testuser=astsplus@fitfond@spt5&mode=list ")
    soup = BeautifulSoup(a, "html.parser" )
    data = {'job': {}}
    info = soup.find_all("div",attrs = {"class" : "data-block"})[1].find_all("div")[0].find_all("div")[2:5]
    for i in info:
        res = re.split(': ', i.get_text())
        data['job'][res[0]] = res[1]
    data['job']['name'] = soup.find_all("h3")[3].string.split(': ')[1]
    mes = json.loads(urllib.request.urlopen("http://10.50.1.35:8080/ui/standsstatus").read())
    for item in mes:
        if item['stand'] == "astsplus@fitfond@spt5":
            if item['status']:
                data['job']['status'] = "Стенд занят:" + item['test']
            else:
                data['job']['status'] = "Стенд свободен"
    last_date = soup.find_all("div", attrs = {"class": "data-block"})[1].find_all("div")[0].find_all("div")[5]
    date = last_date.find("a").get_text()
    last_date.a.decompose()
    res_name = last_date.get_text().strip().replace(":", "")
    data['job'][res_name] = date.strip().split("\n")[0]
    if cur_id != data['job']['Последний тест на данном стенде']: 
        names = []
        k = 0
        for name in soup.find_all("h3")[6:14]:
            names.append(name.string)
        name_index = 0
        for table in soup.find_all("table")[1:9]:
            name = names[name_index]
            data[name] = {"PASSED" : 0, 'WARNING' : 0, 'FAILED' : 0, "ERROR" : 0}
            for tr in table.find_all("tr"):
                i  = tr.find_all("td")[2].find_all("div")[1]
                i.a.decompose()
                i.div.decompose()
                k+= 1
                status  = re.search("\w+", i.get_text()).group(0)
                data[name][status] += 1
            name_index += 1
    else:
        return None
    return(data)

if __name__ == '__main__':
    update()
