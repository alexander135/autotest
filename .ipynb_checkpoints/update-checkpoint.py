import requests
import urllib
import re
import json
import pickle
import yaml
import pymongo
import pprint
from datetime import datetime
import os
import logging
import logging.config

os.chdir(os.path.dirname(os.path.abspath(__file__)))

config = yaml.load(open('config.yaml'))
logger_dict = config['logger_config']
logging.config.dictConfig(logger_dict)
logger = logging.getLogger('server.updating_script')
db_logger = logging.getLogger('server.updaring_script.bd')


def update():
    logger.info('updating script started')
    for curname in config['name'].keys():
        curpath = config['PATH'] + curname + '/lastCompletedBuild/api/python?pretty=true'
        cur = eval(urllib.request.urlopen(curpath).read())
        if int(cur['id']) != (config['name'][curname]['id']):
                logger.info('some new results were found')
                names = []
                res = {"job":{'name': curname,'id':int(cur['id']), 'date': datetime.utcfromtimestamp(cur['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')}}
                path = config['PATH'] + curname + '/' + cur['id'] + '/' + curname+ 'Report/api/python?pretty=true'
                obj = eval(urllib.request.urlopen(path).read())
                for i in obj['suites'][0]['cases']:
                    name = re.findall(r'\..+\.', i['className'])[0].split('.')[1]
                    if name not in res.keys():
                        names.append(name)
                        res[name] = {'passed':0, 'failed':0, 'skipped':0, 'total':0}
                    res[name]['total'] += 1
                    if i['skipped'] == False:
                        if i['status'] != 'FAILED':
                            res[name]['passed'] += 1
                        else:
                            res[name]['failed'] += 1
                    else:
                        res[name]['skipped'] += 1

#                for name in names:
#                    res[name]['succeed'] = round(res[name]['passed']/(res[name]['passed'] + res[name]['failed'])*100, 2)

                with open(curname + '.json', 'w') as file:
                          json.dump(res, file)

                pk = mongoSave(res,curname)

                config['name'][curname]['id'] = int(cur['id'])
                config['name'][curname]['pk'] = pk
                
                
                with open('config.yaml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)

                logger.info('test results have been updated')
                return 'Done'
        else:
            logger.info('already up to date')
            return 0
        
        
def mongoSave(result, jobname):
    db_logger.info('saving to db')
    conn = pymongo.MongoClient()
    db_logger.info('established connection to db')
    db = conn.testresults
    coll = db[jobname]
    result['job']['pk'] = coll.find().count() + 1
    coll.insert_one(result)
    db_logger.info('saved to db')
    return result['job']['pk']
    
if __name__ == '__main__':
    update()