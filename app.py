import json
import os
from flask import Flask, request, render_template
from pymongo import MongoClient
import requests


# pylint: disable=C0103
app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Flask!"

# Getting Database cluster 
connection = os.environ.get("CONNECTION_STRING")
client = MongoClient(connection)


# Route name convention
@app.post('/mongoInsert')
def index():
    db = client.flask_db
    collection = db.fluttereasyaccess
    headers = {
    'Access-Control-Allow-Origin': '*'
    }
    if request.method=='POST':
        dict = {
            "timeStamp" : request.json["timeStamp"],
            "sensorType" : request.json["sensorType"],
            "Channel_1" : request.json["Channel_1"]
        }
        json_object = json.dumps(dict, indent = 4)

        jsonLoad = json.loads(json_object)
        collection.insert_one(jsonLoad)
        return {"Success": 'Data has been added'}, 201, headers
    else:
        return{'error': 'Request must be json'}, 400, headers

# Route for flutter exclusive
@app.post('/flutterInsert')
def postFlutter():
    db = client.flask_db
    collection = db.flutterexclusive
    headers = {
    'Access-Control-Allow-Origin': '*'
    }

    if request.method=='POST':
        dict = {
            "timeStamp" : request.json["timeStamp"],
            "sensorType" : request.json["sensorType"],
            "Channel_1" : request.json["Channel_1"]
        }
        json_object = json.dumps(dict, indent = 4)

        jsonLoad = json.loads(json_object)
        collection.insert_one(jsonLoad)
        return {"Success": 'Data has been added'}, 201, headers
    else:
        return{'error': 'Request must be json'}, 400, headers

# Route To get data
@app.get('/getData')
def getData():
    
    db = client.flask_db
    collection = db.fluttereasyaccess
    headers = {
    'Access-Control-Allow-Origin': '*'
    }
    data = collection.find()
    dataArr = []
    for document in data:
        allData = {
            "timeStamp": document["timeStamp"],
            "sensorType" : document["sensorType"],
            "Channel_1" : document["Channel_1"]
        }
        dataArr.append(allData)

    return {"All_Data":dataArr}, 201, headers


# Route to get flutter data
@app.get('/flutterData')
def flutterData():
    db = client.flask_db
    collection = db.flutterexclusive
    headers = {
    'Access-Control-Allow-Origin': '*'
    }
    data = collection.find()
    dataArr = []
    for document in data:
        allData = {
            "timeStamp": document["timeStamp"],
            "sensorType" : document["sensorType"],
            "Channel_1" : document["Channel_1"]
        }
        dataArr.append(allData)

    return {"All_Data":dataArr}, 201, headers




# Route for puller inserts
@app.post('/pullerInsert')
def postPullerData():
    headers = {
    'Access-Control-Allow-Origin': '*'
    }
    
    requestData = request.json["Channel_1"][2:]
    deviceName = request.json["deviceName"]
    serialNumber = request.json["serialNumber"]
    sensorType = request.json["sensorType"]

    print(f"device name = {deviceName}\nserial Number = {serialNumber}")

    endpoint = f"https://supabase-webservice-tnxbi5wsma-uc.a.run.app/usage/get/device/{deviceName}/{serialNumber}"
    response = requests.get(url=endpoint)
    resJson = response.json()
    if(not resJson):
        return{'error': 'No such usageid'}, 400, headers
    usage_id = resJson["Usage"][0]["usage_id"]
    db = client[deviceName]
    collection = db[usage_id]

    # Splitting the data being received 
 
    initialSplit = requestData.split("\\n")[:-1]
  
    data=[]

    for element in initialSplit:
        data.append(json.loads(element))

    if request.method=='POST':
        collection.insert_many(data)
        collection.update_many(
                {},
                [ 
                    { 
                        "$set": 
                        { 
                            "Sensor Type": sensorType
                        } 
                    },

                    { 
                        "$unset": 
                        [
                            "sampleNum",
                            "tagLEDC1_PD1", 
                            "tagLEDC1_PD2", 
                            "tagLEDC2_PD1", 
                            "tagLEDC2_PD2",  
                            "tagLEDC3_PD1", 
                            "tagLEDC3_PD2", 
                            "tagLEDC4_PD1", 
                            "tagLEDC4_PD2",
                            "LEDC1_PD1", 
                            "LEDC1_PD2", 
                            "LEDC2_PD1", 
                            "LEDC2_PD2",  
                            "LEDC3_PD1", 
                            "LEDC3_PD2", 
                            "LEDC4_PD1", 
                            "LEDC4_PD2",
                            "temperature",
                            "RTC",
                            "sensor",
                            "regAddr",
                            "val",
                            "I2Caddr",
                            "Unnamed: 27"
                        ]
                    }, 
    
                ]
            )
        return {"Success": 'Data has been added'}, 201, headers
    else:
        return{'error': 'Request must be Post'}, 400, headers

# Route To get data
@app.get('/flutterManyData')
def flutterManyData():
    
    db = client.flask_db
    collection = db.fluttermanyexclusive
    headers = {
    'Access-Control-Allow-Origin': '*'
    }
    data = collection.find()
    dataArr = []
    for document in data:
        allData = {
            "timeStamp": document["timeStamp"],
            "sensorType" : document["sensorType"],
            "Channel_1" : document["Channel_1"]
        }
        dataArr.append(allData)

    return {"All_Data":dataArr}, 201, headers

# Technohealth Device insertion 

@app.post('/technohealthInsert')
def postManyTechnohealth():
    db = client.Technohealth
    
    headers = {
    'Access-Control-Allow-Origin': '*'
    }

    if request.method=='POST':
        requestData = request.json["data"]
        # Splitting the data being received 

        initialSplit = requestData.split("\n")[:-1]
        

        # Setting the dictionary keys fir data storage
        keys = ["Usage Id", "Sensor Type", "Timestamp", "Data"]
        # List to store all values
        values = []
        # List of all dictionaries we are going to store in the database 
        data = []
        
        # Get the values from the data we have received 
        for i in initialSplit:
            pairs = i.split(":",1)
            # Dictionary cannot have duplicate keys, so we don't use the keys
            # So we just don't use them, we have our own keys 
            values.append(pairs[1])
        collectionName = str(values[0])
        # Loop to make dictionaries using the keys list and the values
        for i in range(0, len(values), len(keys)):
            value = values[i:i+len(keys)]
            dictionary = dict(zip(keys, value))
            # Storing all the dictionaries into a list
            data.append(dictionary)
        
        # Loop to change all the dictionaries to JSON objects
        # for i in data:
        #     json.dumps(i)
        collection = db[collectionName]
        collection.insert_many(data)

        collection.update_many(
            {},
            [ 

                { 
                    "$unset": ["Usage Id"]
                }, 
            ]
        )
        return {"Success": 'Data has been added'}, 201, headers
    else:
        return{'error': 'Request must be Post'}, 400, headers

# Route to get Technohealth data
@app.get('/<device_name>/<usage_id>')
def technohealthData(device_name,usage_id):
    db = client[device_name]
    collectionName = usage_id
    collection = db[collectionName]
    # For later we can add the usage Id to the url so we can get specific usageID data
    headers = {
    'Access-Control-Allow-Origin': '*'
    }

    if(device_name == "Technohealth"):
        eeg = collection.find(
            {"Sensor Type": "EEG"}
        )
        ppg = collection.find(
            {"Sensor Type": "PPG"}
        )
        eegData = []
        ppgData = []

        dataArr = []
        for document in eeg:
            eegData.append({"Timestamp": document["Timestamp"],
                    "Data" : document["Data"]})
        for document in ppg:
            ppgData.append({"Timestamp": document["Timestamp"],
                    "Data" : document["Data"]})
        
        allData = {
            0:{"EEG": eegData},
            1:{"PPG": ppgData}
        }
        return {"All_Data":allData}, 201, headers
    
    data = collection.find()
    accxData = []
    accyData = []
    acczData = []
    for document in data:
        accxData.append({"Timestamp": document["timestamp"],
                "Data" : document["ACCX"]})
    for document in data:
        accyData.append({"Timestamp": document["timestamp"],
                "Data" : document["ACCY"]})
    for document in data:
        acczData.append({"Timestamp": document["timestamp"],
                "Data" : document["ACCZ"]})
    allData = {
        0:{"ACCX": accxData},
        1:{"ACCY": accyData},
        2:{"ACCZ": acczData}
    }
    
# print(allData["EEG"][1]["Timestamp"])
    return {"All_Data":allData}, 201, headers


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
