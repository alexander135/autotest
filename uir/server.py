from flask import Flask, render_template, redirect, url_for, request, abort

import json
import yaml
import pymongo
from update import update as upd
import os
import logging
import logging.config
import threading, time
app = Flask(__name__)


config = yaml.load(open('config.yaml'))
logger_conf = yaml.load(open('logger_conf.yaml'))
logger_dict = logger_conf['logger_config']
logging.config.dictConfig(logger_dict)
logger = logging.getLogger('server')
logger.info('server started')


conn = pymongo.MongoClient(config['db']['host'], config['db']['port'])


def scheduler(time, updating_scripts):
    t= threading.Timer(time,scheduler,[time, updating_scripts])
    t.start()
    for script in updating_scripts:
        script(conn)

scheduler(3600.0, [upd])



@app.route("/")
def index():
    config = yaml.load(open('config.yaml'))
    names = config['name']
    return render_template('index.html', jobnames = names)


@app.route("/jobs/<jobname>/<pk>")
def present(jobname, pk):
    config = yaml.load(open('config.yaml'))
    pk = int(pk)
    if pk > config['name'][jobname]['pk']:
        abort (404)
    if request.args.get('mes', None):
        message = request.args.get('mes', None)
    else:
        message = ''
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
    if upd(conn)[jobname]:
        config = yaml.load(open('config.yaml'))
        return redirect(url_for('present',jobname = jobname, pk = config['name'][jobname]['pk'], mes = 'done'))
    else:
        return redirect(url_for('present',jobname = jobname, pk = pk, mes = 'already up to date'))



if __name__ == '__main__':
    app.run(host = 'web', port = '80', debug = True, use_reloader = False)
