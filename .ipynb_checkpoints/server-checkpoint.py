from flask import Flask, render_template, redirect, url_for, request
import json
import yaml
import pymongo
from update import update as upd
from crontab import CronTab
import os


app = Flask(__name__)



my_cron = CronTab(user = True) # 2 crons after first run???
my_cron.remove_all()
job = my_cron.new(command='/anaconda3/bin/python /Users/alexandroleshko/uir/update.py') #fix python and script paths
job.minute.every(1)
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
    return render_template('res.html', results = c, pk = pk, last_id = last_id, total = total, message = message)


@app.route("/jobs/<jobname>/<pk>/update")
def update(jobname, pk):
    config = yaml.load(open('config.yaml'))
    if upd():
        return redirect(url_for('present',jobname = jobname, pk = config['name'][jobname]['pk'], mes = 'done'))
    else:
        return redirect(url_for('present',jobname = jobname, pk = pk, mes = 'already up to date'))



if __name__ == '__main__':
    app.run(port = '5000', debug = True)