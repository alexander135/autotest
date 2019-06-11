from flask import Flask, render_template, redirect, url_for, request
import json
import yaml
import pymongo
from update import update as upd
from crontab import CronTab
import os
import logging
import logging.config


app = Flask(__name__)

config = yaml.load(open('config.yaml'))
logger_conf = yaml.load(open('logger_conf.yaml'))
logger_dict = logger_conf['logger_config']
logging.config.dictConfig(logger_dict)
logger = logging.getLogger('server')
logger.info('server started')


my_cron = CronTab(user = True) # 2 crons after first run???
my_cron.remove_all()
job = my_cron.new(command='/anaconda3/bin/python /Users/alexandroleshko/uir/update.py') #fix python and script paths
job.minute.every(1)
logger.info('job started')
my_cron.write()



@app.route("/")
def index():
    config = yaml.load(open('config.yaml'))
    names = config['name']
    return render_template('index.html', jobnames = names)


@app.route("/jobs/<jobname>/<pk>")
def present(jobname, pk):
    config = yaml.load(open('config.yaml'))
    pk = int(pk)
    if request.args.get('mes', None):
        message = request.args.get('mes', None)
    else:
        message = ''
    conn = pymongo.MongoClient()
    db = conn.testresults
    coll = db[jobname]
    total = coll.find().count()
    c = coll.find_one({"job.pk": pk})
    last_id = config['name'][jobname]['id']
    script_time = config['last_update']
    for test_name in c:
        if test_name != 'job' and test_name != '_id':
            c[test_name]['succeed'] = round(c[test_name]['passed'] / (c[test_name]['passed'] + c[test_name]['failed']) * 100, 2)
    
    
    summed_res = {}    
    for type in config['name'][jobname]['to_sum']:              #create dict with summed tests from config
        sum_name =''
        summed = {}
        for i in config['name'][jobname]['to_sum'][type]:
            if sum_name != '':
                sum_name += '+'
            sum_name += i
            for j in c[i].keys():
                if j not in summed.keys():
                    summed[j] = c[i][j]
                else:
                    summed[j] += c[i][j]
        summed_res[sum_name] = summed
        summed_res[sum_name]['succeed'] = round(summed_res[sum_name]['passed'] /\
                                                (summed_res[sum_name]['passed'] + summed_res[sum_name]['failed']) * 100, 2)
                
                
    return render_template('res.html',last_update = script_time, results = c, pk = pk, last_id = last_id, total = total, message = message, summed_res = summed_res)


@app.route("/jobs/<jobname>/<pk>/update")
def update(jobname, pk):
    if upd():
        config = yaml.load(open('config.yaml'))
        return redirect(url_for('present',jobname = jobname, pk = config['name'][jobname]['pk'], mes = 'done'))
    else:
        return redirect(url_for('present',jobname = jobname, pk = pk, mes = 'already up to date'))



if __name__ == '__main__':
    app.run(port = '5000', debug = True)