from flask import Flask,request,session,jsonify,abort
import json
import sqlite3
import sqlalchemy as sql
from sqlalchemy import Table,Column, String, Integer
from datetime import datetime as dt
from multiprocessing import Value
import re

import requests

app = Flask(__name__)
counter=Value('i',0)

@app.errorhandler(405)
def method_not_found(e):
	path=request.path
	if(path=='/api/v1/rides):
		counter.value+=1
		requests.post('http://54.89.184.193:80/api/v1/db/read')
		return jsonify({}),405


@app.route('/api/v1/rides', methods = ['POST'])
def create_ride():
		counter.value+=1
		if (request.method == 'POST'):
				created_by = request.get_json()["created_by"]	
				timestamp = request.get_json()["timestamp"]
				source = request.get_json()["source"]
				destination = request.get_json()["destination"]
                #user_in_db = db.session.query(User).filter(User.username==created_by)
                #user_exist = requests.get('http://my-load-balancer-621305378.us-east-1.elb.amazonaws.com/ap')
                #if not user_exist:
                #               print('cant reach elb')
                #
                #              return {}, 400
                
				rquery = {"table":"UserDetails","column":["username"],"cond":"username='" + created_by + "'"}
				user_exist = requests.post('http://54.89.184.193:80/api/v1/db/read',json=rquery) 
				#res = json.loads(user_exist.text)
				if user_exist.text!=None:
						query = {"op":"add","table":"RideDetails","column":["created_by","timestamp","source","destination"],"add":[created_by,timestamp,source,destination],"cond":""}
						ride = requests.post('http://54.89.184.193:80/api/v1/db/write',json=query)
                       
                        #count_in_db = db.session.query(count)
						return jsonify({}),201
				else:
						print("username doesn't exist")
						return jsonify({}),400
    
@app.route('/api/v1/rides/<int:ride_id>', methods=['DELETE','POST'])
def del_ride(ride_id):
		counter.value+=1
		if(request.method=='DELETE'):
				
				rquery = {"table":"RideDetails","column":["created_by","timestamp","source","destination"],"cond":"ride_id=" + str(ride_id)}
				ride = requests.post('http://54.89.184.193:80/api/v1/db/read',json=rquery)
				if ride.text!=None:
					query = {"op":"delete","table":"RideDetails","column":[],"cond":"ride_id=" + str(ride_id)}
					del_user = requests.post('http://54.89.184.193:80/api/v1/db/write',json=query)
                
                	#count_in_db = db.session.query(count)
					return jsonify({}),200
				else:
					return jsonify({}),400
		else:
				return jsonify({}),405

@app.route('/api/v1/rides/<int:ride_id>', methods=['GET'])
def details_ride(ride_id):
		counter.value+=1
		if(request.method=='GET'):
				
				rquery = {"table":"RideDetails","column":["ride_id","created_by","timestamp","source","destination"],"cond":"ride_id=" + str(ride_id)}
				rides = requests.post('http://54.89.184.193:80/api/v1/db/read',json=rquery)
				print(rides.text)
				if rides.text==None:
					return jsonify(""),204
				else:
					res = json.loads(rides.text)
          
					return jsonify(res)
				return {},200
		else:
		
				return jsonify({}),405



@app.route('/api/v1/rides',methods=['GET'])
def upcoming_ride():
		counter.value+=1
		if (request.method == 'GET'):
				source = request.args['source']
				destination = request.args['destination']
				query={"table":"RideDetails","column":["ride_id","created_by","timestamp","source","destination"],"cond":"source='" + source + "'" and "destination='" + destination + "'"}
				sd_in_db= requests.post('http://54.89.184.193:80/api/v1/db/read',json=query)
				print(sd_in_db.text)
				if sd_in_db.text==None:
					abort(400)
				else:

						d = []
						res = json.loads(sd_in_db.text)
						for i in res:
							dt_time = dt.strptime(i[2],"%d-%m-%Y:%S-%M-%H")
							if dt_time > dt.now():
								d.append({"ride_id":i[0],"created_by":i[1],"timestamp":i[2],"source":i[3],"destination":i[4]})
                        
                        #count_in_db = db.session.query(count)
						return jsonify(d)
		else:
				return jsonify({}),405



@app.route('/api/v1/rides/<int:ride_id>',methods = ['POST'])
def join_ride(ride_id):
		counter.value+=1
		if (request.method=='POST'):
				
				rquery1 = {"table":"RideDetails","column":["ride_id","created_by","timestamp","source","destination"],"cond":"ride_id=" + str(ride_id)}
				rideid_in_db = requests.post('http://54.89.184.193:80/api/v1/db/read',json=rquery1) 
				username = request.get_json()["username"]
				res = json.loads(rideid_in_db.text)
				print(res)
				print(username)
				rquery = {"table":"UserDetails","column":["username","password"],"cond":"username='" + username + "'"}
				user_in_db = requests.post('http://54.89.184.193:80/api/v1/db/read',json=rquery)   
				if user_in_db.text!=None and rideid_in_db.text!=None:
						query={"op":"add","table":"JoinRide","column":["ride_id","created_by"],"add":[ride_id,username],"cond":""}
						join_ride = requests.post('http://54.89.184.193:80/api/v1/db/write',json=query)
						return jsonify({}),201
						
				else:
						abort(400)
						
		else:
				return jsonify({}),405

@app.route('/api/v1/rides/count',methods=['GET','POST','PUT','DELETE'])
def rides_count():
	counter.value+=1
	if(request.method=='GET'):
		query={"table":"RideDetails","column":["created_by","timestamp","source","destination"],"cond":""}
		rides_in_db = requests.post('http://54.89.184.193:80/api/v1/db/read',json=query)
		count = len(rides_in_db.text)
		return jsonify([count]),200
	else:
		return jsonify({}),405
		
@app.route('/api/v1/_count',methods=['GET'])
def http_count():
	if(request.method=='GET'):
		with counter.get_lock():
			L=[counter.value]
		return jsonify(L),200
		
@app.route('/api/v1/_count',methods=['DELETE'])
def count_delete():
	if(request.method=='DELETE'):
		with counter.get_lock():
			counter.value=0
			L=[counter.value]
		return {},200


if __name__ == "__main__":

    #from server import app
    
    
	app.debug=True
	app.run(port=5000)

# with counter.get_lock():
#       counter.value+=1






