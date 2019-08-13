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


config = yaml.full_load(open('config.yaml'))
logger_conf = yaml.full_load(open('logger_conf.yaml'))
logger_dict = logger_conf['logger_config']
logging.config.dictConfig(logger_dict)
logger = logging.getLogger('server.updating_script')
db_logger = logging.getLogger('server.updating_script.bd')



password_mgr = urllib.request.HTTPPasswordMgrWithPriorAuth()
top_level_url = "http://asts-jenkins.moex.com/"
password_mgr.add_password(None, top_level_url, os.environ['jen_login'], os.environ['jen_pass'], is_authenticated = True)
handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
opener = urllib.request.build_opener(handler)
urllib.request.install_opener(opener)


def update(conn, flag = False):

    with open('lock.txt', 'w') as f:
        f.write('locked')
    res = {}
    result = {}
    logger.info('updating script started')
    config = yaml.full_load(open('config.yaml'))
    config['last_update'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    with open('config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    for curname in config['jobs'].keys():
        curpath = '/'.join([config['PATH'], curname, 'lastCompletedBuild/api/python?pretty=true'])
        cur = eval(urllib.request.urlopen(curpath).read())
        if not conn.testresults[curname].count() or (int(cur['id']) != (config['jobs'][curname]['id'])):     
                        path = '/'.join([config['PATH'],curname, cur['id'],'testReport/api/python?pretty=true'])
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
                                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
                            continue 

                        logger.info(curname + ' some new results were found')

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
                                
                                params = eval(urllib.request.urlopen(top_level_url + subbuild['url'] + 'api/python?pretty=true').read())['actions'][0]['parameters']
                                TDIR = list(filter(lambda x: x['name'] == 'TDIR', params))[0]['value'].split('/')[0]
                                obj = eval(urllib.request.urlopen(path).read())
                                if TDIR not in res.keys():
                                    res[TDIR] = {'passed':obj['passCount'], 'failed':obj['failCount'], 'skipped':obj['skipCount'], 'total':obj['skipCount'] + obj['passCount'] + obj['failCount']}
                                else:
                                    res[TDIR]['passed'] += obj['passCount']
                                    res[TDIR]['skipped'] += obj['skipCount']
                                    res[TDIR]['failed'] += obj['failCount']
                                    res[TDIR]['total'] += obj['skipCount'] + obj['passCount'] + obj['failCount']
                        except:
                            logger.info('job has no subjobs')
                            obj = eval(urllib.request.urlopen(path).read())
                            count_res(obj, res)

                                                                    
                        soup = BeautifulSoup(urllib.request.urlopen('/'.join([config['PATH'], curname, cur['id'], 'parameters/'])), "html.parser")
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
                            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

                        logger.info('test results have been updated')
                        result[curname] = 'Done'
        else:
                        logger.info(curname + ' already up to date')
                        result[curname] = 0
    for lcov in config['LCOV'].keys():
        res = update_LCOV(str(config['LCOV'][lcov]['id']))
        if res:
            logger.info(lcov + "new results were found")
            result[lcov] = "Done"
            pk = mongoSave(res, lcov, conn)

            logger.info([res['job']['Date'],type(res['job']['Date'])])
            config["LCOV"][lcov]['id'] = str(res['job']['Date'])
            config["LCOV"][lcov]['pk'] = pk
            with open("config.yaml", 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        else:
            result[lcov] = 0
            logger.info(lcov + "already up to date")

    
    for name in config['FI_curr_RHEL6'].keys():
        try:
            problems = conn.testresults[name].find_one({"job.pk": config['FI_curr_RHEL6'][name]['pk']})['problems']
        except:
            problems = None
        logger.info(problems)
        method, res = update_FI(config['FI_curr_RHEL6'][name]['id'], problems)
        logger.info(method)
        if res:
            if method == 'update':
                mongoUpdate(res, name, conn)
                result[fi] = 'Updated problem'
            else:
                res['job']['name'] = name
                pk = mongoSave(res, name, conn)
                result[name] = 'Done'
                config['FI_curr_RHEL6'][name]['id'] = res['job']['Дата запуска']
                config['FI_curr_RHEL6'][name]['pk'] = pk
                with open('config.yaml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        else:
            result[name] = 0
            logger.info(name + "already up to date")

    
    
    if flag:
        for name in config['stand'].keys():
            res = update_stand(config['stand'][name]['id'])
            if res:
                pk = mongoSave(res, name, conn)
                result[name] = 'Done'
                config['stand'][name]['id'] = res['job']['Последний тест на данном стенде']
                config['stand'][name]['pk'] = pk
                with open('config.yaml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
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
   

def mongoUpdate(result, name, conn):
    db_logger.info('saving to db')
    db = conn.testresults
    db_logger.info('established connection to db')
    coll = db[name]
    coll.update_one({'job.pk' : result['job']['pk']}, {'problems' : result['problems']})
    db_logger.info('updated problems')
    return None




    
def update_one(jobname, pk, conn):    
    config = yaml.full_load(open('config.yaml'))
    res = conn.testresults[jobname].find_one({"job.pk": int(pk)})
    logger.info(res)
    path = '/'.join([config['PATH'], jobname, str(res['job']['id']), 'testReport/api/python?pretty=true'])
    try:
        urllib.request.urlopen(path)
    except:
        logger.critical(path + ' error ')
        return False
    soup = BeautifulSoup(urllib.request.urlopen('/'.join([config['PATH'], jobname, str(res['job']['id']), 'parameters/'])), "html.parser")
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
    config = yaml.full_load(open('config.yaml'))
    a = urllib.request.urlopen('/'.join([config["stand_PATH"], "generic/stand?testuser=astsplus@fitfond@spt5&mode=list "]))
    soup = BeautifulSoup(a, "html.parser" )
    data = {'job': {}}
    info = soup.find_all("div",attrs = {"class" : "data-block"})[1].find_all("div")[0].find_all("div")[2:5]
    for i in info:
        res = re.split(': ', i.get_text())
        data['job'][res[0]] = res[1]
    data['job']['name'] = soup.find_all("h3")[3].string.split(': ')[1]
    mes = json.loads(urllib.request.urlopen('/'.join([config['stand_PATH'], "standsstatus"])).read())
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
                try:
                    i.div.decompose()
                except:
                    pass
                k+= 1
                status  = re.search("\w+", i.get_text()).group(0)
                if status != "RUNNING":
                    data[name][status] += 1
            name_index += 1
    else:
        return None
    return(data)


def update_LCOV(cur_id):
    logger.info('updating LCOV')
    page = urllib.request.urlopen("http://asts-jenkins.moex.com/view/Coverage/job/lcov.rebus-curr.build/ws/coverage.report/index.html")
    
    logger.info("connected")
    soup = BeautifulSoup(page, "html.parser")

    res = {'job' : {}}
    tds = soup.find_all("td", attrs = {"class" : "headerItem"})
    for td in tds:
        if td.next_sibling.next_sibling['class'][0] == "headerValue":
            if str(td.string) != "Current view:":
                res['job'][str(td.string).strip(":")] = td.next_sibling.next_sibling.string
        else:
            cur = td.next_sibling.next_sibling
            numbers = []
            while cur:
                numbers.append(cur.string)
                cur = cur.next_sibling.next_sibling
            res[str(td.string).strip(":")] = numbers
    logger.info([res,cur_id])
    if res['job']['Date'] != cur_id:
        return res
    else:
        return None


def update_FI(cur_id, cur_problems):
    logger.info('updating FI') 
    page = urllib.request.urlopen("http://10.50.170.25/ui/lastrun?testuser=fitrebus6")
    logger.info('connected to FI')
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
    logger.info(data)

    if data['job']['Дата запуска'] == cur_id and cur_problems != None:
        if data['problems'] == cur_problems:
            return None, None
        return "update", data
    return 'insert', data
    

if __name__ == '__main__':
    update()
