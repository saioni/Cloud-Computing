from flask_sqlalchemy import SQLAlchemy
from flask import Flask,request,session,jsonify,abort
import json
import sqlite3
from sqlalchemy import Column, String, Integer
from datetime import datetime
from models import connect_to_db,User,Ride,upcoming_rides,ride_details,join_exist

app = Flask(__name__)


def sha(passwo):
    if len(passwo) != 40:
        return False
    try:
        sha1 = int(passwo,16)
    except ValueError:
        return False
    return True

@app.route('/api/v1/users', methods = ['PUT'])
def new_user():
    username = request.get_json()['username']
    password = request.get_json()['password']

    user_in_db = db.session.query(User).filter(User.username==username).all()
    if not user_in_db:
        check = sha(password)
        if check:
            add_user = User(username=username, password=password)
        
            db.session.add(add_user)
            db.session.commit()
            return jsonify({}),201
        else:
            return jsonify({}),400
    else:
        return jsonify({}),400


@app.route('/api/v1/users', methods=['DELETE'])

def del_user():
    username = request.get_json()['username']
    user_in_db = db.session.query(User).filter(User.username==username)
    if str(user_in_db.first()) == username:
        user_in_db.delete()
        db.session.commit()
        return jsonify({}),200
    else:
        return jsonify({}),400
    

@app.route('/api/v1/rides', methods = ['POST'])
def create_ride():
    if (methods == 'POST'):
        created_by = request.get_json()["created_by"]
        timestamp = request.get_json()["timestamp"]
        source = request.get_json()["source"]
        destination = request.get_json()["destination"]
        user_in_db = db.session.query(User).filter(User.username==created_by)
        if not user_in_db:
            return jsonify({}),400
        else:
            new_trip = Ride(created_by=created_by,timestamp=timestamp,source=source,destination=destination)
            db.session.add(new_trip)
            db.session.commit()
            return jsonify({}),201
    else:
        return jsonify({}),405


@app.route('/api/v1/rides?source={source}&destination={destination}', methods = ['GET'])
def upcoming_ride():
    if (methods == 'GET'):
        ride_id = request.get_json()["ride_id"]
        username = request.get_json()["username"]
        timestamp = request.get_json()["timestamp"]
        user_ride = db.session.query(Ride).filter(Ride.created_by==username)
        if not user_ride:
            return jsonify(),400
        else:
            #fetch from create_rides
        
    else:
        return jsonify({}),405


@app.route()
def details_rides():
    ride_id = request.get_json()[]
    
   
        
if __name__ == "__main__":

    #from server import app
    connect_to_db(app)
    db.create_all()
    print("connected to db")
    
    app.debug=True
    app.run(port=5000, host="0.0.0.0")


    


    


    

    
