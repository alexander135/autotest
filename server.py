from flask import Flask, render_template
import json
import pickle
import plotly
app = Flask(__name__)

@app.route("/")
def hello():
    with open('results.json', 'r') as file:
        res = json.load(file)
    return render_template('res.html', results = res)

if __name__ == '__main__':
    app.run(port = '5000', debug = True)