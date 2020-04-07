#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 13:15:52 2020
Company : LK Consulting
@author: LK
"""
import queue as q 
import serial
import time
import threading as Task

S = []
R = []

SendQueSize = 512
ReceiveQueSize = 4096

for i in range(3):
    S.append(q.Queue(SendQueSize))
    R.append(q.Queue(ReceiveQueSize))
    
cmds = [b"a01HELLO",b"a03HELLO",b"a51HELLO",b"a44HELLO",b"a55HELLO",
        b"a03GPIOA1",b"a51GPIOA1",b"a03GPIOB1",b"a51GPIOB1",b"a03GPIOC1",b"a51GPIOC1",
        b"a03GPIOA0",b"a51GPIOA0",b"a03GPIOB0",b"a51GPIOB0",b"a03GPIOC0",b"a51GPIOC0",
        b"a03ANAA",b"a51ANAA",b"a03ANAB",b"a51ANAB",b"a44BUTTON",b"a55BUTTON"]

baud = 9600                # baud rate
port = '/dev/ttyAMA0'       # serial URF port on this computer

ser = serial.Serial(port, baud,timeout=2.0,write_timeout=3.0)
ser.close()
ser.open() 
ser.flushOutput()
ser.flushInput()    
verbose = False
class jemRFSend(Task.Thread):
    def __init__(self,ids,name):
        Task.Thread.__init__(self)
        self.name = name
        self.sendQue = S[ids]     
        self.ser = ser
        self.timeout = 0.3
        return
#   def sendCommand(self,ids,cmd,param1):    
    def sendCommand(self,querry):
#        querry = bytes(querry,'utf8')
#        querry = b"a"+bytes(ids,'utf8')+bytes(cmdTable[cmd],'utf8')+bytes(param1,'utf8') 
#        querry = "a"+str(ids)+cmdTable[cmd],param1 
        try :
            a = self.ser.write(querry) 
        except serial.SerialTimeoutException:
            print("write timeout ",querry, '  err:', a)
        except:
            print("write went wrong" ,querry, '  err:', a)
        return
 
    def run(self):
        while(True):
            msg = self.sendQue.get()
            if verbose :
                print(msg)
            self.sendCommand(msg)
            time.sleep(self.timeout)
        return
class jemRFReceive(Task.Thread):
    def __init__(self,ids,name):
        Task.Thread.__init__(self)
        self.name = name
        self.recQue = R[ids]        
        self.ser = ser
        self.timeout = 0.05
        self.ec = 0
        self.bc = 0
        self.hl = 0
        self.gpio = 0
        self.ana = 0
        self.button = 0
        self.started = 0
        return
 
    def recCommand(self):
        RESLENGTH = 13
        a = self.ser.inWaiting()
        if a == 0 :
            return None
        while (self.ser.read(1) != b'a') :
            print('not b a')
            continue
        time.sleep(self.timeout)
        res = b'a'+self.ser.read(RESLENGTH-1)
        if len(res) != RESLENGTH:
            print("error in response:", res)
            return None
        now = time.strftime("%c") 
        if res[3:6] == b"ERR":
            self.ec += 1
        elif res[3:7]==b"BATT":
            self.bc += 1
            return None
        elif res[3:7] == b"GPIO":
            self.gpio += 1
        elif res[3:6] == b"ANA":
            self.ana += 1
        elif res[3:8] == b"HELLO":
            self.hl += 1
        elif res[3:9] == b"BUTTON":
            self.button += 1
        elif res[3:10] == b"STARTED":
            self.started += 1
            return None
#            print(str(res),'  :',now)
        return({"res":res,"time":now})

    def run(self):
        while(True):
            a = self.recCommand()
            if (a != None):
                self.recQue.put(a)
        time.sleep(0.3)                
        return


#                self.recQue.put({"res":res,"time":now})
ts = jemRFSend(0,"SEND")                
tr = jemRFReceive(0,"RECEIVE") 
 
 
 
ts.start()
tr.start()
