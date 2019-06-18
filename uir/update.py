import urllib.request
import re
import json
import yaml
import pymongo
from datetime import datetime
import os
import logging
import logging.config

os.chdir(os.path.dirname(os.path.abspath(__file__)))


#TODO change PATH or curname to add noRebus jobs
#Special tests in to_sum config.yaml fix time
#bootstrap?? design, little js(выпадающие окошки, пофиксить надпись об обновлении)

config = yaml.load(open('config.yaml'))
logger_conf = yaml.load(open('logger_conf.yaml'))
logger_dict = logger_conf['logger_config']
logging.config.dictConfig(logger_dict)
logger = logging.getLogger('server.updating_script')
db_logger = logging.getLogger('server.updaring_script.bd')


password_mgr = urllib.request.HTTPPasswordMgrWithPriorAuth()
top_level_url = "http://asts-jenkins.moex.com/"
password_mgr.add_password(None, top_level_url, config['user']['username'], config['user']['password'], is_authenticated = True)
handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
opener = urllib.request.build_opener(handler)
urllib.request.install_opener(opener)


def update(conn):
    res = {}
    logger.info('updating script started')
    config = yaml.load(open('config.yaml'))
    config['last_update'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    with open('config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    for curname in config['name'].keys():
        curpath = config['PATH'] + curname + '/lastCompletedBuild/api/python?pretty=true'
        cur = eval(urllib.request.urlopen(curpath).read())
        if conn.testresults[curname].count():
                logger.info(conn.testresults[curname].count())
                if int(cur['id']) != (config['name'][curname]['id']):     
                        logger.info('some new results were found')
                        names = []
                        res = {"job":{'name': curname,'id':int(cur['id']), 'date': datetime.fromtimestamp(cur['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')}}
                        path = config['PATH'] + curname + '/' + cur['id'] + '/testReport/api/python?pretty=true'
                        obj = eval(urllib.request.urlopen(path).read())
                        for i in obj['suites'][0]['cases']:
                            name = re.findall(r'\..+\.', i['className'])[0].split('.')[1]
                            if name not in res.keys():
                                names.append(name)
                                res[name] = {'passed':0, 'failed':0, 'skipped':0, 'total':0}
                            res[name]['total'] += 1
                            if i['skipped'] == False:
                                if (i['status'] != 'FAILED') and (i['status'] != 'REGRESSION'):
                                    res[name]['passed'] += 1
                                else:
                                    res[name]['failed'] += 1
                            else:
                                res[name]['skipped'] += 1



                        pk = mongoSave(res,curname,conn)

                        config['name'][curname]['id'] = int(cur['id'])
                        config['name'][curname]['pk'] = pk
                        
                        
                        with open('config.yaml', 'w') as f:
                            yaml.dump(config, f, default_flow_style=False)

                        logger.info('test results have been updated')
                        res[curname] = 'Done'
                else:
                        logger.info('already up to date')
                        res[curname] = 0
        else:
                logger.info('some new results were found')
                names = []
                res = {"job":{'name': curname,'id':int(cur['id']), 'date': datetime.fromtimestamp(cur['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')}}
                path = config['PATH'] + curname + '/' + cur['id'] + '/testReport/api/python?pretty=true'
                obj = eval(urllib.request.urlopen(path).read())
                for i in obj['suites'][0]['cases']:
                    name = re.findall(r'\..+\.', i['className'])[0].split('.')[1]
                    if name not in res.keys():
                        names.append(name)
                        res[name] = {'passed':0, 'failed':0, 'skipped':0, 'total':0}
                    res[name]['total'] += 1
                    if i['skipped'] == False:
                        if (i['status'] != 'FAILED') and (i['status'] != 'REGRESSION'):
                            res[name]['passed'] += 1
                        else:
                            res[name]['failed'] += 1
                    else:
                        res[name]['skipped'] += 1



                pk = mongoSave(res,curname,conn)

                config['name'][curname]['id'] = int(cur['id'])
                config['name'][curname]['pk'] = pk
                
                
                with open('config.yaml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)

                logger.info('test results have been updated')
                res[curname] = 'Done'
    return res 
 

def mongoSave(result, jobname, conn):
    db_logger.info('saving to db')
    db = conn.testresults
    db_logger.info('established connection to db')
    coll = db[jobname]
    result['job']['pk'] = coll.find().count() + 1
    coll.insert_one(result)
    db_logger.info('saved to db')
    return result['job']['pk']
    
if __name__ == '__main__':
    update()
