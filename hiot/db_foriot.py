#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 20:20:55 2020
Company : LK Consulting
@author: LK
"""
 
import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")

myhiotdb = myclient["HIOT"]
myhiotfsm = myhiotdb["FSM"]
myhiotlog = myhiotdb['LOG']
myhiotdata = myhiotdb["IO"]
myhomedb = myhiotdb["HOME"]
mysensordb = myhiotdb["SENSOR"]

 
for x in myhiotdata.find():
    print(x) 

for x in myhiotlog.find():
    print(x) 
 
myfsmlist = [
        
        {"_id":1,"name":"FSM1","polling rate": 100},
        {"_id":2,"name":"FSM2","polling rate": 100}
 
        ]        
x = myhiotfsm.insert_many(myfsmlist)

for y in myhiotfsm.find():
    print(y) 

RFFLEX = {"Read" :{"ANAA":0,"ANAB":0},
          "SetDO":{"GPIOA":"0","GPIOB":"0","GPIOC":"0"}
          }
 

homelist = [
        {"add":"San Jose1",
         "name":"LK1",
         "mobile":"408-999-9999",
         "username" :"LK1",
         "password":"abcxyz"},
        {"add":"San Jose2",
         "name":"LK2",
         "mobile":"408-777-7777",
         "username" :"LK2",
         "password":"abcxyz"}        
        ]
sensorlist = [
        {"add":"San Jose1",
         "device0":{"id":"01","config":"MASTER"},
         "device1":{"id":"03","config":"RFFLEX"},
         "device2":{"id":"51","config":"RFFLEX"},
         "device3":{"id":"44","config":"SWITCH"},
         "device4":{"id":"55","config":"SWITCH"},
         "device5":{"id":"None"},
         "sensor0":{"name":"UV1","type":"AI","id":"03","io":"ANNA","loc":{"major":"CH1","minor1":"WAFER","minor2":"CENTER"}},
         "sensor1":{"name":"UV2","type":"AI","id":"03","io":"ANAB","loc":{"major":"CH1","minor":"WAFER","minor2":"MIDDLE1"}},
         "sensor2":{"name":"DO1","type":"DO","id":"03","io":"GPIOA","loc":{"major":"CH1","minor1":"GAS1","minor2":"FINAL"}},
         "sensor3":{"name":"DO2","type":"DO","id":"03","io":"GPIOB","loc":{"major":"CH1","minor1":"GAS2","minor2":"FINAL"}},
         "sensor4":{"name":"DO3","type":"DO","id":"03","io":"GPIOC","loc":{"major":"CH1","minor1":"GAS3","minor2":"FINAL"}},
         "sensor5":{"name":"UV3","type":"AI","id":"51","io":"ANNA","loc":{"major":"CH1","minor1":"WAFER","minor2":"MIDDLE2"}},
         "sensor6":{"name":"UV4","type":"AI","id":"51","io":"ANAB","loc":{"major":"CH1","minor":"WAFER","minor2":"EDGE"}},
         "sensor7":{"name":"DO4","type":"DO","id":"51","io":"GPIOA","loc":{"major":"CH1","minor1":"GAS4","minor2":"FINAL"}},
         "sensor8":{"name":"DO5","type":"DO","id":"51","io":"GPIOB","loc":{"major":"CH1","minor1":"GAS5","minor2":"FINAL"}},
         "sensor9":{"name":"DO6","type":"DO","id":"51","io":"GPIOC","loc":{"major":"CH1","minor1":"GAS6","minor2":"FINAL"}},
         "sensor10":{"name":"SWITCH1","type":"DI","id":"44","io":"BUTTON","loc":{"major":"CH1","minor1":"Interlock1","minor2":"LID"}},
         "sensor11":{"name":"SWITCH2","type":"DI","id":"55","io":"BUTTON","loc":{"major":"CH1","minor1":"Interlock2","minor2":"HalfA"}},
         "sensor12":{"id":"None"},
        },
        {"add":"San Jose2",
         "device0":{"id":"01","config":"MASTER"},
         "device1":{"id":"04","config":"RFFLEX"},
         "device2":{"id":"52","config":"RFFLEX"},
         "device3":{"id":"None"},
         "sensor0":{"name":"UV1","type":"AI","id":"04","io":"ANNA","loc":{"major":"CH1","minor1":"WAFER","minor2":"CENTER"}},
         "sensor1":{"name":"UV2","type":"AI","id":"04","io":"ANNB","loc":{"major":"CH1","minor":"WAFER","minor2":"MIDDLE"}},
         "sensor2":{"name":"DO1","type":"DO","id":"04","io":"GPIOA","loc":{"major":"CH1","minor1":"GAS1","minor2":"FINAL"}},
         "sensor3":{"id":"None"},
        }        
        ]
x = myhomedb.insert_many(homelist)    
print("home inserted : ",x)  
y = mysensordb.insert_many(sensorlist) 
print("sensor inserted : ",y)
""" 

for x in myhiotlog.find():
    print(x) 
"""
print("search")

x = myhomedb.find_one({"add":"San Jose1" })
print(x["add"])
y = mysensordb.find_one({"add":x["add"]})
print(y)
print(y["device0"]["id"],"    ",y["sensor0"]["loc"])
 