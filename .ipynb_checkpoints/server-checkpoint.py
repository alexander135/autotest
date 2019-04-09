from flask import Flask, render_template
import json
import pickle
import plotly
import yaml
import pymongo

app = Flask(__name__)

config = yaml.load(open('config.yaml'))

@app.route("/")
def index():
    names = config['name']
    return render_template('index.html', jobnames = names)


@app.route("/jobs/<jobname>/<id>")
def present(jobname, id):
    id = int(id)
    conn = pymongo.MongoClient()
    db = conn.testresults
    coll = db[jobname]
    c = coll.find_one({"job.id": id})
    last_id = config['name'][jobname]
    return render_template('res.html', results = c, id = id, last_id = last_id)


@app.route("/update")
def update():
    #todo update test results
    pass



if __name__ == '__main__':
    app.run(port = '5000', debug = True)