from flask import Flask, render_template, redirect, url_for, request, abort

import json
import yaml
import pymongo
from update import update as upd
from update import update_one
import os
import logging
import logging.config
import threading, time
from collections import OrderedDict

from forms import CommentForm, ColorConfigForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'

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


@app.route("/jobs/<jobname>/<pk>", methods = ['GET', 'POST'])
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
    c = coll.find_one({"job.pk" : pk})
    dict_for_sum = coll.find_one({"job.pk" : pk})
    form = CommentForm()
    color_config_form = ColorConfigForm()
    if color_config_form.validate_on_submit():
        config['name'][jobname]['color']['bot'] = color_config_form.bot.data
        config['name'][jobname]['color']['top'] = color_config_form.top.data
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return redirect('')
    color_config_form.bot.data = config['name'][jobname]['color']['bot']
    color_config_form.top.data = config['name'][jobname]['color']['top']
    if 'comment' in c['job'].keys():
        form.comment.data = c['job']['comment']
    prev = coll.find_one({"job.pk" : pk-1})
    last_id = config['name'][jobname]['id']
    script_time = config['last_update']
    for test_name in c:
        if test_name != 'job' and test_name != '_id':
            c[test_name]['succeed'] = round(c[test_name]['passed'] / (c[test_name]['passed'] + c[test_name]['failed']) * 100, 2)
            if c[test_name]['succeed'] <= config['name'][jobname]['color']['bot']:
                c[test_name]['color'] = 'bg-danger'
            elif c[test_name]['succeed'] >= config['name'][jobname]['color']['top']:
                c[test_name]['color'] = 'bg-success'
            else:
                c[test_name]['color'] = 'bg-warning'
            if prev:
                dif = c[test_name]['total'] - prev[test_name]['total']
                if dif>=0:
                    dif = '+' + str(dif)
                c[test_name]['total'] = str(c[test_name]['total']) + '(' + str(dif) + ")"
            
    
    
    summed_res = {} 
    flag = False
    for type in config['name'][jobname]['to_sum']:              #create dict with summed tests from config
        sum_name =''
        summed = {}
        for i in config['name'][jobname]['to_sum'][type]:
            if i in dict_for_sum.keys():
                if sum_name != '':
                    sum_name += '+'
                sum_name += i
                for j in dict_for_sum[i].keys():
                    if j not in summed.keys():
                        summed[j] = dict_for_sum[i][j]
                    else:
                        summed[j] += dict_for_sum[i][j]
        if sum_name != '':
            summed_res[sum_name] = summed
            summed_res[sum_name]['succeed'] = round(summed_res[sum_name]['passed'] /\
                                                (summed_res[sum_name]['passed'] + summed_res[sum_name]['failed']) * 100, 2) 
            if summed_res[sum_name]['succeed'] <= config['name'][jobname]['color']['bot']:
                summed_res[sum_name]['color'] = 'bg-danger'
            elif summed_res[sum_name]['succeed'] >= config['name'][jobname]['color']['top']:
                summed_res[sum_name]['color'] = 'bg-success'
            else:
                summed_res[sum_name]['color'] = 'bg-warning'
    return render_template('res.html',form = form, color_config_form = color_config_form, last_update = script_time, results = OrderedDict(sorted(c.items())), pk = pk, last_id = last_id, total = total, message = message, summed_res = summed_res)


@app.route("/jobs/<jobname>/<pk>/update")
def update(jobname, pk):
    if upd(conn)[jobname]:
        config = yaml.load(open('config.yaml'))
        return redirect(url_for('present',jobname = jobname, pk = config['name'][jobname]['pk'], mes = 'done'))
    else:
        return redirect(url_for('present',jobname = jobname, pk = pk, mes = 'already up to date'))


@app.route("/jobs/<jobname>/<pk>/editComment", methods = ['GET', 'POST'])
def comment(jobname,pk):
    form = CommentForm()
    logger.info(form.validate_on_submit())
    if form.validate_on_submit():
        db = conn.testresults
        db[jobname].update_one({"job.pk": int(pk)}, {"$set": {'job.comment' : form.comment.data}}, upsert = False)
        return form.comment.data
    return form.comment.data

@app.route("/test")
def replace():
    k = 0
    config = yaml.load(open('config.yaml'))
    for name in config['name']:
        total = conn.testresults[name].find().count()
        for i in range(1, total+1):
            update_one(name,i,conn)
            k+=1
    return str(k);




if __name__ == '__main__':
    app.run(host = 'web', port = '80', debug = True, use_reloader = False)

