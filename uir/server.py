from flask import Flask,flash, render_template, redirect, url_for, request, abort

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
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

from forms import ConfigForm, CommentForm, OptionsForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = b'\x1c\x97\x16\x8ar\xd3\xe9U\x1bs\xc8"\x06\x84\x10\xa5'

login_manager = LoginManager()
login_manager.init_app(app)

config = yaml.load(open('config.yaml'))
logger_conf = yaml.load(open('logger_conf.yaml'))
logger_dict = logger_conf['logger_config']
logging.config.dictConfig(logger_dict)
logger = logging.getLogger('server')
logger.info('server started')


conn = pymongo.MongoClient(config['db']['host'], config['db']['port'])
if os.path.exists("lock.txt"):
    os.remove("lock.txt")

def scheduler(time, updating_scripts):
    t= threading.Timer(time,scheduler,[time, updating_scripts])
    t.start()
    for script in updating_scripts:
        script(conn)

scheduler(3600.0, [upd])




class User(object):
    def __init__(self, username = "", password = ""):
        self.username = username
        self.password = password

    def get_id(self):
        return (self.username)        

    def get(username):
        if conn.testresults.users.find_one({"name": username}):
            return User(username, conn.testresults.users.find_one({"name": username})['password'])
        else:
            return None
        
    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/")
def index():
    config = yaml.load(open('config.yaml'))
    jobnames = config['jobs']
    names = config['stand']
    return render_template('index.html', jobnames = jobnames, names = names)


@app.route("/<name>/<jobname>/<pk>", methods = ['GET', 'POST'])
def present(name, jobname, pk):
    config = yaml.load(open('config.yaml'))
    try:
        pk = int(pk)
    except:
        abort(404)
    if pk > config[name][jobname]['pk']:
        abort (404)
    if request.args.get('mes', None):
        message = request.args.get('mes', None)
    else:
        message = ''
    db = conn.testresults
    coll = db[jobname]
    total = coll.find().count()
    c = coll.find_one({"job.pk" : pk})
    form = CommentForm()
    options_form = OptionsForm()
    jobnames = config['jobs'].keys()
    names = config['stand'].keys()
    path = config['PATH']
    if 'comment' in c['job'].keys():
        form.comment.data = c['job']['comment']
    if name == 'stand':
        c['total'] = {"PASSED" : 0, 'WARNING' : 0, 'FAILED' : 0, "ERROR" : 0, "total_group": 0}
        for testname in c:
            if testname!= 'job' and testname != '_id':
                c[testname]['total_group'] = c[testname]['WARNING'] + c[testname]['PASSED'] + c[testname]['FAILED'] + c[testname]['ERROR']
                if testname != 'total':
                    for status in c[testname]:
                        c['total'][status] += c[testname][status]

        return render_template('stand_res.html',path = path,name = name, jobnames = jobnames, names = names, pk = pk, total = total, results = c, form = form, message = message)

    data = {'date': [],'passed':[], 'skipped':[], 'failed':[]}      # data for line-chart                                   
    if 'parameters' in c['job'].keys():
        cur_data_count = 0
        for item in db[jobname].find().sort('job.pk', pymongo.DESCENDING):
            if 'parameters' in item['job'].keys():
                if 'GITREVISION' not in c['job']['parameters'].keys() or item['job']['parameters']['GITREVISION'] == c['job']['parameters']['GITREVISION']:
                    if cur_data_count >= config[name][jobname]['chart_data_count']:
                        break
                    for test_name in item:
                        if test_name != '_id' and test_name != 'job':
                            for status in item[test_name]:
                                if status != 'total':
                                    if len(data[status]) == cur_data_count:
                                        data[status].append(item[test_name][status])
                                    else:
                                        data[status][cur_data_count] += item[test_name][status]
                    cur_data_count+=1
                    data['date'].append([item['job']['date'], item['job']['id'], item['job']['pk']])




    for key in data.keys():
        data[key].reverse()

    dict_for_sum = coll.find_one({"job.pk" : pk})


    if options_form.validate_on_submit():
        config[name][jobname]['color']['bot'] = options_form.bot.data
        config[name][jobname]['color']['top'] = options_form.top.data
        config[name][jobname]['chart_data_count'] = options_form.count.data
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return redirect('')

    options_form.bot.data = config[name][jobname]['color']['bot']
    options_form.top.data = config[name][jobname]['color']['top']
    try:
        options_form.count.data = config[name][jobname]['chart_data_count']
    except: 
        options_form.count.data = 20

    prev = coll.find_one({"job.pk" : pk-1})
    last_id = config[name][jobname]['id']
    script_time = config['last_update']
    for test_name in c:
        if test_name != 'job' and test_name != '_id':
            c[test_name]['succeed'] = round(c[test_name]['passed'] / (c[test_name]['passed'] + c[test_name]['failed']) * 100, 2)
            if c[test_name]['succeed'] <= config[name][jobname]['color']['bot']:
                c[test_name]['color'] = 'bg-danger'
            elif c[test_name]['succeed'] >= config[name][jobname]['color']['top']:
                c[test_name]['color'] = 'bg-success'
            else:
                c[test_name]['color'] = 'bg-warning'
            if prev:
                if test_name in prev.keys():
                    dif = c[test_name]['total'] - prev[test_name]['total']
                    if dif>=0:
                        dif = '+' + str(dif)
                    c[test_name]['total'] = str(c[test_name]['total']) + '(' + str(dif) + ")"
            
    
    
    summed_res = {} 
    flag = False
    for type in config[name][jobname]['to_sum']:              #create dict with summed tests from config
        sum_name =''
        summed = {}
        for i in config[name][jobname]['to_sum'][type]:
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
            if summed_res[sum_name]['succeed'] <= config[name][jobname]['color']['bot']:
                summed_res[sum_name]['color'] = 'bg-danger'
            elif summed_res[sum_name]['succeed'] >= config[name][jobname]['color']['top']:
                summed_res[sum_name]['color'] = 'bg-success'
            else:
                summed_res[sum_name]['color'] = 'bg-warning'
    return render_template('res.html', names=names,name = name, jobnames = jobnames, path = path, chart_data = data, form = form, options_form = options_form, last_update = script_time, results = OrderedDict(mysort(c.items())), pk = pk, last_id = last_id, total = total, message = message, summed_res = summed_res)

@app.route("/<name>/<jobname>/<pk>/update")
def update(name, jobname, pk):
    if not os.path.exists("lock.txt"):
        if upd(conn, name == 'stand')[jobname]:
            config = yaml.load(open('config.yaml'))
            return redirect(url_for('present',name = name, jobname = jobname, pk = config[name][jobname]['pk'], mes = 'done'))
        else:
            return redirect(url_for('present',name = name, jobname = jobname, pk = pk, mes = 'already up to date'))
    else:
        return redirect(url_for('present',name = name, jobname = jobname, pk = pk, mes = 'already up to date'))


@app.route("/<name>/<jobname>")
def red(name, jobname):
    conifg = yaml.load(open("config.yaml"))
    return redirect(url_for("present", name = name, jobname = jobname, pk = config[name][jobname]['pk']))




@app.route("/<name>/<jobname>/<pk>/editComment", methods = ['GET', 'POST'])
def comment(name, jobname,pk):
    form = CommentForm(request.form)
    if not form.validate():
        response = {"status" : False, "errors": form.errors}
        return json.dumps(response)
    if form.validate_on_submit():
        db = conn.testresults
        db[jobname].update_one({"job.pk": int(pk)}, {"$set": {'job.comment' : form.comment.data}}, upsert = False)
        return json.dumps({"comment":form.comment.data, "status":True})
    return form.comment.data

@app.route("/test")
def replace():
    k = 0
    config = yaml.load(open('config.yaml'))
    for nam in config[name]:
        total = conn.testresults[nam].find().count()
        for i in range(1, total+1):
            update_one(nam,i,conn)
            k+=1
    return str(k);


@app.route("/login", methods =['GET', 'POST']) 
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and not form.validate():
            return json.dumps({"status":False, "errors": form.errors})
    if form.validate_on_submit():
            if User.get(form.login.data):
                curUser = User.get(form.login.data)
                if form.password.data == curUser.password:
                    login_user(curUser)
                    return json.dumps({'status': True})
                form.password.errors.append('wrong password')
            else:
                form.login.errors.append('wrong name')
            return json.dumps({"status":False, "errors": form.errors})
    return render_template("login.html", login_form = form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/changeConf", methods = ["GET", "POST"])
@login_required
def changeConf():
    form = ConfigForm(request.form)
    config = yaml.load(open('test_config.yaml'))
    if form.validate_on_submit():
        config = form.config.data
        with open('config.yaml', 'w') as f:
            f.write(config)
        return redirect(url_for("index"))
    with open("config.yaml", "r") as f:
        data = ''.join(f.readlines())
    form.config.data = data
    return render_template("changeConf.html", configForm = form, config = config)


def mysort(mas):
    types = ["Tests","FunctionalTests" ,"SpecialTests", "SmokeTests"]
    for item in mas:
        if item[0] == "Tests":
            yield item
    for item in mas:
        if item[0] == "SmokeTests":
            yield item
    for item in mas:
        if item[0] == "FunctionalTests":
            yield item
    for item in mas:
        if item[0] == "SpecialTests":
            yield item
    for item in mas:
        if item[0] not in types:
            yield item

if __name__ == '__main__':
    app.run(host = 'web', port = '8080', debug = True, use_reloader = False)

