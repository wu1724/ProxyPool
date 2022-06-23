import random
import threading
from json import dumps

import requests
from flask import Flask, render_template, request
from threading import Thread
from core.engine import Engine
from configs import data_ip_path, logger_path

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_proxy_json')
def get_proxy_json():
    r = engine.get_proxy(mode='json')
    r = dumps(r)
    return r


@app.route('/get_proxy_txt', methods=['POST', 'GET'])
def get_proxy_txt():
    r = engine.get_proxy()
    return r


@app.route('/get_all_proxy', methods=['GET'])
def get_all_proxy():
    rs = engine.db.get_all()
    rs = {'num': len(rs), 'proxys': rs}
    rs = dumps(rs)
    return rs


@app.route('/proxys')
def proxys_list():
    rs = engine.db.get_all(0, 10, 1.5)
    num = len(rs)
    return render_template('proxys.html', num=num, proxys=rs)


@app.route('/check_all')
def check_all():
    engine.check_all()


@app.route('/<ip>:<port>')
def check(ip, port):
    rs = engine.checker.check('http', ip, port)
    rs = dumps(rs)
    return rs


if __name__ == "__main__":
    engine = Engine(data_ip_path, logger_path)
    t = Thread(target=engine.run, name='engine')
    t.start()
    app.run(host="0.0.0.0", port=52394)

    t.join()
