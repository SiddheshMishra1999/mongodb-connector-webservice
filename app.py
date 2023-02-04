import json
import os
from flask import Flask, request, render_template
from pymongo import MongoClient

# pylint: disable=C0103
app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Flask!"

# Getting Database cluster 
connection = os.environ.get("CONNECTION_STRING")
client = MongoClient(connection)
db = client.flask_db
collection = db.fluttereasyaccess

# Route name convention
@app.post('/mongoInsert')
def index():
    if request.method=='POST':
        dict = {
            "timeStamp" : request.json["timeStamp"],
            "sensorType" : request.json["sensorType"],
            "Channel_1" : request.json["Channel_1"]
        }
        json_object = json.dumps(dict, indent = 4)

        jsonLoad = json.loads(json_object)
        collection.insert_one(jsonLoad)
        return {"Success": 'Data has been added'}, 201
    else:
        return{'error': 'Request must be json'}, 400

@app.get('/getData')
def getData():
    data = collection.find()
    dataArr = []
    for document in data:
        allData = {
            "timeStamp": document["timeStamp"],
            "sensorType" : document["sensorType"],
            "Channel_1" : document["Channel_1"]
        }
        dataArr.append(allData)

    return {"All_Data":dataArr}, 201

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
