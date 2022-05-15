import time
import json
import requests
from flask import Flask, jsonify, request
from sqlalchemy import null
from process import *
import sys
import logging

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route('/time', methods=['GET'])
def get_current_time():
    response = jsonify({'time': time.time()})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response




global tfidf
global content_data
global list_app_name

@app.route('/setup')
def setup():
    global tfidf
    global content_data
    global list_app_name
    content_data = set_up()
    tfidf, list_app_name = tf_idf(content_data)
    return {}


@app.route("/get_game",methods=['POST'])
def get_game():
    global tfidf
    global content_data
    global list_app_name
    # testing
    # user_profile = [["DARK SOULS III", 286], ['Grand Theft Auto V', 45], ['Portal 2', 8], ['RESIDENT EVIL 7 biohazard  BIOHAZARD 7 resident evil', 88], ['Sekiro Shadows Die Twice', 1.4]]
    data = json.loads(request.get_data())
    user_profile = list(map(list, zip(data['games'], data['playTimes'])))
    result = get_recommendation(user_profile, content_data, tfidf, list_app_name)
    return jsonify({'recommend' : result})

    # data是前端返回的JSON数据，包含名称和时间
    # 加入Jupyter note的后端代码计算返回数据
    # 包括读取数据集的所有游戏
    # 返回推荐游戏名称

    # api在前端的react调用方式通过flask + react
    # flask端口是 http://127.0.0.1:5000/get_game or http://localhost:5000/get_game
    # 后端启动方式yarn start-api
    # 前端启用可以改成 yarn start
