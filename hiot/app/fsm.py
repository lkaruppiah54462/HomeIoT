# -*- coding: utf-8 -*-
"""
Spyder Editor
Company : LK Consulting
@author: LK
"""
#import numpy as np
import time as t
import queue as q 
import threading as Task



M = []
G = []
MsgQueSize = 512
GuiQueSize = 4096
DefaultPollingRate = 100/1000
for i in range(10):
    M.append(q.Queue(MsgQueSize))
    G.append(q.Queue(GuiQueSize))

class lkFSM():
    def __init__(self,id,stateList,name):  
        Task.Thread.__init__(self)
        self.name = name
        self.msgQue = M[id]
        self.guiQue = G[id]
        self.currentState = "PowerUp"
        self.previousState = "PowerUp"
        self.pollingRate = DefaultPollingRate #in ms
        self.stateStartTimetick = None
        self.currentTimeTick = None
        self.fsmStateList = stateList
        return
    def lKFSMStateSwitch(self,msg):
        if (self.fsmStateList[self.currentState].get(msg["MM"])==None):
            print("invalid  stae switch: ","current state  ","message received:",msg)  
            return
        func = getattr(self,self.currentState+"Leave")
        func()
        tempState = self.fsmStateList[self.currentState][msg["MM"]]
        if msg.get("PARAMS") != None:
            self.PARAMS = msg.get("PARAMS")
            print(self.PARAMS)            
        else:
            self.PARAMS = None
        self.previousState = self.currentState
        self.currentState = tempState
        self.stateStartTimeTick = t.time()  #seconds
        func = getattr(self,self.currentState+"Entry")
        if self.socket != None :
            msg = {'pstate':self.previousState,'cstate':self.currentState}
            self.socket.emit('state',msg,broadcast = True)         
        func()
        return
    
    def lkFSMStateUpdate(self):
        try :
            #msg is the Msg XXXX
            msg = self.msgQue.get(block=True,timeout = self.pollingRate) 
        except q.Empty:
#            if ( not q.Empty):
#                print("que not empty")
#            print (e)
#            if (e == q.Empty):
            func = getattr(self,self.currentState+"Polling")
            func()
            self.currentTimeTick = t.time()

            return
#        else :
#                print("unknown exception :",self.name)
#                return
        self.lKFSMStateSwitch(msg)
        return

    def run(self): 
#        ipdb.set_trace()
        func = getattr(self,self.currentState+"Entry")
        func()
        while(True):
            self.lkFSMStateUpdate() 
            
        