# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 22:23:05 2020
Company : LK Consulting
@author: LK
"""
import threading as Task
from app import fsm
from app import serialsendrec as ssr
#from app import __init__ as ini
#import fsm as fsm
#from numpy import interp	# To scale values
#from flask import Flask, render_template
#from flask_socketio import SocketIO, emit
import time

#import json
#import logging
#app = Flask(__name__)
#log = logging.getLogger('werkzeug')
#log.disabled = True

import pymongo as mdb
myclient = mdb.MongoClient("mongodb://localhost:27017/")
myhiotdb = myclient["HIOT"]
myhiotfsm = myhiotdb["FSM"]
myhiotlog = myhiotdb['LOG']
myhiotdata = myhiotdb["IO"]
myhomedb = myhiotdb["HOME"]
mysensordb = myhiotdb["SENSOR"]
verbose = False
cmdTable = { "UP":"+++",
            "AIA":"ANAA",
            "AIB":"ANAB",
            "CHDEVID":"CHDEVID",
            "HELLO":"HELLO",
            "WAKE":"WAKE",
            "AWAKE":"AWAKE",
            "NOMSG":"NOMSG",
            "RESET":"RESET",
            "GPIO":"GPIO",
            "REBOOT":"REBOOT",
            "TYPE":"TYPE",
            "BUTTON":"BUTTON",
            "BATT":"BATT"}

resTable = {"UP":"OK",
          "AIA":"ANAA",
          "AIB":"ANAB",
          "CHDEVID":"CHDEVID",
          "HELLO":"HELLO",
          "WAKE":"WAKE",
          "AWAKE":"AWAKE",
          "NOMSG":"NOMSG",
          "RESET":"RESET",
          "GPIO":"GPIO",
          "REBOOT":"REBOOT",
          "TYPE":"TYPE",
          "BUTTON":"BUTTON",
          "BATT":"BATT"
          }

#database stuff (mongodb)
 


serRFStateTable  = {'PowerUp': {'Msg Idle': 'Idle', 'Msg PowerUp': 'PowerUp'},
 'Idle': {'Msg Idle': 'Idle','Msg Listen':'Listen','Msg Screen CMD':'ScreenCMD',  'Msg Online': 'Online',  'Msg PowerUp': 'PowerUp','Msg Stop': 'Stop'},
 'Online': {'Msg Idle': 'Idle', 'Msg Online': 'Online','Msg PowerUp': 'PowerUp','Msg Stop': 'Stop'},
 'Stop': {'Msg Idle': 'Idle',  'Msg PowerUp': 'PowerUp','Msg Stop': 'Stop'},
 'Listen': {'Msg Idle': 'Idle','Msg PowerUp': 'PowerUp','Msg Listen':'Listen'},
 'ScreenCMD': {'Msg Idle': 'Idle', 'Msg Screen CMD':'ScreenCMD', 'Msg PowerUp': 'PowerUp','Msg Stop': 'Stop'}}
def logAiData(ai):
        tt = time.asctime(time.localtime())
        timex = "time"
        channel = "ioAI1to4"
        logData = {timex :tt,channel:ai}
        myhiotdata.insert_one(logData)
        return
def logData(id,cmd,io,data):
        tt = time.asctime(time.localtime())
        timex = "time"  
        logData = {timex :tt,"id":id,"cmd":cmd,"io":io,"data":data}
        myhiotdata.insert_one(logData)    
        return
def logBadEvent(id,cmd):
        tt = time.asctime(time.localtime())
        querry = b"a"+bytes(str(id)+cmd,'utf8')
        bevent = "Real Bad :  {}     {}".format(querry,tt)
        print(bevent)
        bevent = {"time":tt,"event" : "Real Bad {}".format(querry)}
        myhiotlog.insert_one(bevent) 
        return
def logBattEvent(cmd):
        tt = time.asctime(time.localtime())  
        bevent = {"time":tt,"event" : "Batt Stat {}".format(cmd)}
        myhiotlog.insert_one(bevent)
        return
class masterRF():
    def __init__(self,ids):
        self.id = ids
        self.cmds = [b"HELLO"]
        self.cmdp = []
        self.name = "MASTER"
        return
    def updateIOData(self,ids,cmd,data):
        if ids != bytes(self.id,'utf8') :
            print("big problems:","obj id:",self.id,"cmd id:",ids)
class rfFlex():
    def __init__(self,ids):
        self.id = ids
        self.cmds = [b"HELLO",b"REBOOT"]
        self.cmdp = [b"ANAA",b"ANAB"]
        self.name = "RFFLEX"
        self.anaa =  0
        self.anab =  0
        self.gpioa = 0
        self.gpiob = 0
        self.gpioc = 0
        return
    def updateIOData(self,ids,cmd,data):
        if ids != bytes(self.id,'utf8') :
            print("big problems:","obj id:",self.ids,"cmd id:",ids)
            return
        if cmd == "":
            return
        if cmd == b"ANAA":
            self.anaa = int(data)
        elif cmd == b"ANAB":
            self.anab = int(data)
        elif cmd == b"GPIOA":
            self.gpioa = int(data)
        elif cmd == b"GPIOB":
            self.gpiob = int(data)       
        elif cmd == b"GPIOC":
            self.gpioc = int(data)            

class switchRF():
    def __init__(self,ids):
        self.id = ids
        self.cmds = [b"HELLO",b"REBOOT"]
        self.cmdp = [b"BUTTON"]
        self.name = "SWITCH"
        self.button = b"OFF"
        return
    def updateIOData(self,ids,cmd,data):
        if ids != bytes(self.id,'utf8') :
            print("big problems:","obj id:",self.ids,"cmd id:",ids)
            return
        if cmd == b"BUTTON":
            self.button = data                
class serRF(fsm.lkFSM,Task.Thread):
    def __init__(self,id,stateList,name):
        fsm.lkFSM.__init__(self,id,stateList,name)
        return
    def findActiveDevice(self,ids):
        for ad in self.activeDevices:
            if bytes(ad.id,'utf8') == ids:
                return ad
        print("ID not found in active device list:",ids)
        return None
    def PowerUpEntry(self):
        print("Power up enter")
        self.output= [[0,0],[0,0]]
        self.socket = None
        self.ts = ssr.ts
        self.tr = ssr.tr
        self.activeDevices = []
        x = myhomedb.find_one({"add":"San Jose1" })
        y = mysensordb.find_one({"add":x["add"]})
        i=0
        while y["device"+str(i)]["id"] != 'None':
            global verbose
            if verbose :
                print(y["device"+str(i)])
            if y["device"+str(i)]["config"] == "MASTER":
                self.activeDevices.append(masterRF(y["device"+str(i)]["id"]))
            elif y["device"+str(i)]["config"] == "RFFLEX":
                self.activeDevices.append(rfFlex(y["device"+str(i)]["id"]))
            elif y["device"+str(i)]["config"] == "SWITCH":
                self.activeDevices.append(switchRF(y["device"+str(i)]["id"])) 
            i += 1
        for cd in self.activeDevices:
            for cmd in cd.cmds:
                querry = b"a"+bytes(cd.id,'utf8')+cmd
                self.ts.sendQue.put(querry) 
#                time.sleep(0.2)
#        time.sleep(5)                                                  
        return
    def PowerUpPolling(self):
        while self.tr.recQue.qsize() > 0 :    
            msg = self.tr.recQue.get()
            if verbose :
                print(msg)
            if msg["res"][3:6] == b"ERR":
                myhiotlog.insert_one(msg) 
        self.msgQue.put({"MM":"Msg Idle"})
#        print("Power up polling",self.name)        
        return
    def PowerUpLeave(self):
        print("Power up leave")
        return
    def IdleEntry(self):
 
        print("Idle enter")
        return
    def IdlePolling(self):
#        self.msgQue.put({"MM":"Msg Online"})        
        return
     
    def IdleLeave(self):
        print("Idle leave")
        return
    def OnlineEntry(self):
        print("Online enter")
        self.count = 0
        return
    def OnlinePolling(self):
        self.count += 1
        if  self.count%50 != 0 or self.count == 0:
            return
        for cd in self.activeDevices:
            for cmd in cd.cmdp:
                querry = b"a"+bytes(cd.id,'utf8')+cmd
                self.ts.sendQue.put(querry)
#                time.sleep(0.2)
#        time.sleep(3)
        while self.tr.recQue.qsize() > 0 :    
            msg = self.tr.recQue.get()
            if verbose :
                print(msg)
            if msg["res"][3:6] == b"ERR":
                myhiotlog.insert_one(msg)
            cmd = b""
            data =b""
            ids = msg["res"][1:3]
            if msg['res'][3:6] == b"ANA":
                cmd = msg['res'][3:7]
                temp = msg['res'][7:-1].split(b'-',1)
                if (temp[0] == b''):
                    return  
                index = {b"03":0,b"51":1}
                index1 = {b"ANAA":0,b"ANAB":1}                
                l = index[msg['res'][1:3]]
                m =index1[msg['res'][3:7]]
                self.output[l][m] = int(temp[0])
                data = int(temp[0])
            elif msg['res'][3:7] == b"GPIO":
                cmd = msg['res'][3:8]
                data = msg['res'][8:9] 
            elif msg['res'][3:9] == b"BUTTON":
                o = {b"ON-":"ON",b"OFF":"OFF"}
                cmd = msg['res'][3:9]
                data = o[msg['res'][9:12]]

            ret = self.findActiveDevice(ids)
            if ret != None :
                ret.updateIOData(ids,cmd,data)
                if self.socket != None :
                    temp = {"03":"1","51":"2"}
                    if ret.name == "RFFLEX" :
                        msg = {"id":ret.id,"type":ret.name,"data1":ret.anaa,"data2":ret.anab}
                        self.socket.emit('device'+temp[ret.id],msg,broadcast = True)
        return
    def OnlineLeave(self):
        while self.tr.recQue.qsize() > 0 :    
            msg = self.tr.recQue.get()
            print(msg)
            if msg["res"][3:6] == b"ERR":
                myhiotlog.insert_one(msg)            
        print("Online leave")
        return
    def StopEntry(self):
        print("Stop enter")
        return
    def StopPolling(self):
        return
    def StopLeave(self):
        print("Stop leave")
        return
    def ScreenCMDEntry(self):
        print("Screen CMD enter")
        while self.tr.recQue.qsize() > 0 :    
            msg = self.tr.recQue.get()
            print(msg)
            if msg["res"][3:6] == b"ERR":
                myhiotlog.insert_one(msg)    
        self.count = 0
 
        #class fields like id,cmd , ... already setup
        if (self.PARAMS == None ) :
            print('no parameter for screen cmd')
            return
        ids = self.PARAMS["id"]
        cmd = self.PARAMS["cmd"]        
        param1 = self.PARAMS["param1"]
        querry = b"a"+bytes(ids,'utf8')+bytes(cmdTable[cmd],'utf8')+bytes(param1,'utf8')
        self.ts.sendQue.put(querry)        
        return
    def ScreenCMDPolling(self):
        if self.tr.recQue.qsize() > 0 :
            msg = self.tr.recQue.get()
            print(msg) 
            res = msg["res"]
            ids = res[1:3].decode("utf-8")
            paramr = ""
            param1 = self.PARAMS['param1']
            paramw = ""
            a = "OK"
            cmd = self.PARAMS["cmd"]
            if res[3:7] == b"BATT":
                print("BATT:",res)
                return
            elif res[3:6] == b"ERR":
                a = "ERR" 
            elif res[3:7] == b"GPIO":
                cmd = res[3:8].decode("utf-8")
                paramr = res[8:9].decode("utf-8")
            elif res[3:6] == b"ANA":
                cmd = res[3:7].decode("utf-8")
                temp = res[7:-1].split(b'-',1)
                if (temp[0] == b''):
                    return  
                paramr = int(temp[0])
            elif res[3:8] == b"HELLO":
                cmd = res[3:8].decode("utf-8")
                paramr = ""
            elif res[3:9] == b"BUTTON":
                cmd = res[3:9].decode("utf-8")
                temp = res[9:-1].split(b'-',1) 
                paramr = temp[0].decode("utf-8")

            msg = {'id':ids,'cmd':cmd,'paramw':paramw,'paramr':paramr,'param1':param1,'err':a}
            if self.socket != None :
                self.socket.emit(self.PARAMS["ch"],msg,broadcast = True)        
            self.msgQue.put({"MM":"Msg Idle"})
            return
        self.count += 1
        if self.count > 20 :
            msg = {'id':self.PARAMS["id"],'cmd':self.PARAMS["cmd"],'paramw':self.PARAMS["paramw"],'paramr':self.PARAMS['paramr'],'param1':self.PARAMS['param1'],'err':"NORESPONSE"}
            if self.socket != None :            
                self.socket.emit(self.PARAMS["ch"],msg,broadcast = True)                 
            self.msgQue.put({"MM":"Msg Idle"})
            print("screen cmd timedout")            
        return
    def ScreenCMDLeave(self):
        print("Screen CMD leave")
        self.count = 0
    def ListenEntry(self):
        print("Listen enter")
        return
    def ListenPolling(self):
        if self.tr.recQue.qsize() > 0 :    
            msg = self.tr.recQue.get()
            print(msg)        
        return
    def ListenLeave(self):
        print("Listen leave")
        return 
        return
sT = []
#if __name__ == "__main__":

x = myhiotfsm.find_one({"_id": 1})
name = x["name"]
t0 = serRF(0,serRFStateTable,name)
#t0.msgQue.put({"MM":"Msg Idle"})
sT.append(t0)
#time.sleep(5)
sT[0].start()
print("started test0 power up")
 
#    socketio.run(app, host='0.0.0.0')

    


 
 
 
#    socketio.run(app, host='0.0.0.0')

