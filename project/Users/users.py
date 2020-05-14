from flask import Flask,request,session,jsonify,abort
import json
import requests
import sqlalchemy as sql
from sqlalchemy import Table,Column, String, Integer
from datetime import datetime as dt
from multiprocessing import Value
import re


app = Flask(__name__)
counter=Value('i',0)

@app.errorhandler(405)
def method_not_found(e):
	path=request.path
	if(path=='/api/v1/users):
		counter.value+=1
		requests.post('http://54.89.184.193:80/api/v1/db/read')
		return jsonify({}),405

def sha(passwo):
    if len(passwo) != 40:
        return False
    try:
        sha1 = int(passwo,16)
    except ValueError:
        return False
    return True



@app.route('/api/v1/users', methods = ['PUT','POST','DELETE'])
def new_user():
		counter.value+=1
		if(request.method=='PUT'):
				username=request.get_json()["username"]
				password=request.get_json()["password"]
              
				rquery = {"table":"UserDetails","column":["username"],"cond":"username='" + username + "'"}
				user = requests.post('http://54.89.184.193:80/api/v1/db/read',json=rquery)   
				
				if username not in user.text:
						check = sha(password)
						if check:

								rquery1 = {"op":"add","table":"UserDetails","column":["username","password"],"add":[username,password],"cond":""}
								user1 = requests.post('http://54.89.184.193:80/api/v1/db/write',json=rquery1)
                               
								return jsonify({}),201

						else:
								return jsonify({}),400
				else:
						print('not ok')
						return jsonify({}),400
		else:
				return jsonify({}),405



@app.route('/api/v1/users/<username>', methods=['DELETE'])
def del_user(username):	
		counter.value+=1
		if(request.method=='DELETE'): 
			rquery = {"table":"UserDetails","column":["username","password"],"cond":"username='" + username + "'"}
			user = requests.post('http://localhost:80/api/v1/db/read',json=rquery)
			if user.text!=None:
				query={"op":"delete","table":"UserDetails","column":[],"cond":"username='" + username + "'"}
				user = requests.post('http://54.89.184.193:80/api/v1/db/write',json=query)
				return jsonify({}),200
			else:
				return jsonify({}),400
		else:
			return jsonify({}),405

@app.route('/api/v1/users', methods=['GET'])
def list_user():
	counter.value+=1
	if(request.method=='GET'):
		rquery = {"table":"UserDetails","column":["username"],"cond":""}
		user = requests.post('http://54.89.184.193:80/api/v1/db/read',json=rquery)        
		if user.text==None:
			return jsonify(""),204
		else:
			res = json.loads(user.text)
          
			return jsonify(res)
		return {},200
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
			counter.value('i',0)
			L=[counter.value]
		return "",200




if __name__ == "__main__":

    #from server import app
	app.debug = True
	app.run(port=5000)

# with counter.get_lock():
#       counter.value+=1






