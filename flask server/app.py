from flask import Flask, render_template
from flask import request
import hashlib
import json
import csv
import pandas as pd
import os
from werkzeug import secure_filename
from web3 import Web3
from utils import Utils
import pyqrcode

from merkle_tree import MerkleTree
from merkle_tree import TreeNode

ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/dropfile')
def dropfile():
    return render_template('dropfile.html')

@app.route('/uploadfile', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
    	f = request.files['file']
    	f.save(secure_filename("student_data.csv"))
    	filedata = pd.read_csv('student_data.csv')
    	tree = MerkleTree()
    	columns = list(filedata.columns)
    	for i in range(len(filedata)):
    		data = {}
    		for j in range(len(columns)):
    			s = filedata[columns[j]][i]
    			data[columns[j]] = str(s)
    		json_data = json.dumps(data)
    		tree.add(json_data)
    	tree.createTree()
    	Utils.writeToFile("root.txt", Web3.toHex(tree.getMerkleRoot().value))
    	# generate the certificate json with hash and merklepath in header
    	# and data in certificate
    	for i in range(len(filedata)):
    		data = {}
    		header = {}
    		header['hash'] = Web3.toHex(tree.getLeafHash(i))
    		path = []
    		for x in range(len(tree.getMerklePath(i))):
    			path.append(Web3.toHex(tree.getMerklePath(i)[x]))
    		header['merkleproof'] = path
    		data['header'] = header
    		certificateData = {}
    		for j in range(len(columns)):
    			certificateData[columns[j]] = str(filedata[columns[j]][i])
    		data['certificate'] = certificateData
    		json_data = json.dumps(data)
    		Utils.writeToFile(certificateData['ID'] + ".txt", json_data)
    	return render_template('publish.html', roothash = Web3.toHex(tree.getMerkleRoot().value), year = 2014)
    else:
    	return "<image src='static/not_found.png' style='width:100%; height:100%;'/>"

@app.route("/upload")
def upload():
	return render_template("upload.html")

@app.route('/filereader')
def filereader():
    return render_template('filereader.html')

@app.route("/publish")
def publish():
	return render_template("uploadcsv.html")

@app.route('/index')
def index():
	return render_template("index.html")

@app.route("/query")
def hash():
	normalhash = request.args.get('hash')
	privateKey = "0x0bc9b5bf5d3a57829de9c2cc9d82ff3a21b0c6be4f33d9ac19a1807a6f8ef189"
	x = Web3.toHex(Web3.soliditySha3(['bytes32', 'bytes32'], [normalhash, privateKey]))
	#y = Web3.toHex(Web3.soliditySha3(['bytes32'], [x]))
	data = {}
	data['value'] = str(x)
	json_data = json.dumps(data)
	return json_data

@app.route("/equery")
def encrypthash():
	normalhash = request.args.get('hash')
	privateKey = "0x0bc9b5bf5d3a57829de9c2cc9d82ff3a21b0c6be4f33d9ac19a1807a6f8ef189"
	x = Web3.toHex(Web3.soliditySha3(['bytes32', 'bytes32'], [normalhash, privateKey]))
	y = Web3.toHex(Web3.soliditySha3(['string'], [x]))
	data = {}
	data['value'] = str(y)
	json_data = json.dumps(data)
	return json_data

@app.route("/data")
def data():
	read_csv()
	return "Working"

if __name__ == "__main__":
    app.run(debug=True, port=80, threaded=True)
