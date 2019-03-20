from flask import render_template, json, jsonify, Flask, abort, send_from_directory
import connexion
import requests
from openpyxl import load_workbook
from flask import Flask, request, render_template, redirect, url_for
import csv
import flask
import shutil
from tempfile import NamedTemporaryFile
from collections import OrderedDict 
# Create the application instance
ret=[]
app = connexion.App(__name__, specification_dir='./')
@app.route('/',methods=['GET', "POST"])
def home():
    return render_template('home.html')
@app.route('/historical/<date>', methods=['DELETE'])
def removeOne(date):
	ret={}
	data = {}
	fields = ['DATE','TMAX','TMIN']
	temp_file = NamedTemporaryFile(mode='w', delete=False, newline='')
	with open( 'dailyweather.csv', 'r' ) as data_file, temp_file:
		data = csv.DictReader( data_file, fieldnames=fields )
		writer = csv.DictWriter(temp_file, fieldnames=fields)
		for row in data:
			print(row)
			if row['DATE'] != date:
				writer.writerow(row)

	shutil.move(temp_file.name, 'dailyweather.csv')
	return jsonify(), 200
@app.route('/historical/<date>', methods=['GET'])
def get(date):
	ret={}
	with open( 'dailyweather.csv' ) as data_file:	
		data = csv.reader( data_file )
		for row in data:
			if date == row[0]:
				ret["DATE"] = row[0]
				ret["TMAX"] = row[1]
				ret["TMIN"] = row[2]
	if ret == {}:
		return jsonify(), 404
	else:
		return jsonify(ret), 200
# If we're running in stand alone mode, run the application
@app.route('/historical/', methods=['GET', "POST"])
def historical():
	if request.method=="GET":
		ret=[]
		with open( 'weather.json' ) as data_file:
			data = json.load( data_file )
			for item in data:
				ret.append( { "DATE" : item[ "DATE" ] } )
		return jsonify( ret ), 200 
	else:
		data = request.get_json()
		fields = ['DATE','TMAX','TMIN']
		with open(r'dailyweather.csv', 'a', newline='') as data_file:
			writer = csv.DictWriter(data_file, fieldnames=fields)
			writer.writerow(data)
		return jsonify({'DATE':data['DATE']}), 201	
@app.route('/forecast', methods=['GET', "POST"])
def forecast():
	global ret
	if request.method=="GET":
		return jsonify(ret), 200
	else: 
		ret=[]
		date =  request.form["dateName"]
		with open( 'dailyweather.csv' ) as data_file:	
			data = csv.reader( data_file )
			data=sorted(data)
			count=0;
			for row in data:
				if date==row[0] or count==1 or count==2 or count==3 or count==4 or count==5:
					ret.append(row)
					count+=1
			return jsonify(ret), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
