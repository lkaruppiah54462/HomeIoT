#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 22:37:44 2020
Company : LK Consulting
@author: LK
"""
global ts,tr
singletotwo = {
        1:"01",
        2:"02",
        3:"03",
        4:"04",
        5:"05",
        6:"06",
        7:"07",
        8:"08",
        9:"09"        
        }
noyestobool = {
        'No':False,
        'Yes' : True
        }

from flask import Flask,Response
from config import Config
from flask_socketio import SocketIO,emit
import logging
import json
from datetime import datetime
import time
app = Flask(__name__)
app.config.from_object(Config)
print("initxxx")
from flask import render_template


log = logging.getLogger('werkzeug')
log.disabled = True
global socketio
socketio = SocketIO(app)
#from flask import render_template
#from app import app
#from app import fsm
from app import iot


@app.route('/')
def index():
    iot.sT[0].socket = socketio 
    return render_template('index.html')

@socketio.on('connect')
def test_connect():
    emit('after connect',  {'data':'Lets dance'})
    msg = {'pstate':iot.sT[0].previousState,'cstate':iot.sT[0].currentState}
    emit('state',msg,broadcast = True) 
    return
@socketio.on('querry')
def querry(message):
    print('receved querry  ',message['data1'],'::',message['data2'],'::',message['data3'],'::',message['data4']) 
#    iot.sT[0].socket = socketio
    iot.sT[0].msgQue.put({"MM":"Msg Screen CMD","PARAMS":{"id":message['data1'],"cmd":message['data2'],
           "paramw":'',"paramr":noyestobool[message['data3']],"param1":message['data4'],"ch":'res'}})
    return
@socketio.on('querry1')
def querry1(message):
    print('receved querry1 ',message['data1'],'::',message['data2'],'::',message['data3'],'::',message['data4'])

    iot.sT[0].msgQue.put({"MM":"Msg Screen CMD","PARAMS":{"id":message['data1'],"cmd":message['data2'],
           "paramw":'',"paramr":noyestobool[message['data3']],"param1":message['data4'],"ch":'res1'}})
    return
@socketio.on('fsmcmd')
def fsmcmd(message):
    print('receved fsmcmd ',message['data1'])
    iot.sT[0].msgQue.put({"MM":message['data1']})
    return
@app.route('/chart-data')
def chart_data():
    print("chart")
    def getAiData():        
        while True:
            json_data = json.dumps(
                    {'time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'value' : iot.sT[0].output})
            yield f"data:{json_data}\n\n"
            time.sleep(4)
    return Response(getAiData(),mimetype='text/event-stream')

                    
                
                    
 