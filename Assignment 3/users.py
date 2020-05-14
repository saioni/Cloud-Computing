rom flask_sqlalchemy import SQLAlchemy
from flask import Flask,request,session,jsonify,abort
import json
import sqlite3
from sqlalchemy import Column, String, Integer
from datetime import datetime as dt
import requests
from multiprocessing import Value

app = Flask(__name__)
counter=Value('i',0)


db=SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer,autoincrement=True, primary_key = True)
    username = db.Column(db.String(32),index=True)
    password = db.Column(db.String(40))
    def __repr__(self):
        return self.username

class Ride(db.Model):
    __tablename__ = "rides"
    ride_id = db.Column(db.Integer,autoincrement=True, primary_key = True)
    created_by = db.Column(db.String(32),index=True)
    timestamp = db.Column(db.String(50))
    source = db.Column(db.String(40))
    destination = db.Column(db.String(40))
    def __repr__(self):
        return (self.created_by,
                self.timestamp,
                self.source,
                self.destination)

class JoinRide(db.Model):
        __tablename__="joinride"
        joinid = db.Column(db.Integer,autoincrement=True,primary_key=True)
        ride_id = db.Column(db.Integer,index=True)
        username = db.Column(db.String(32),index=True)
        def __repr__(self):
                (self.username,
                self.ride_id)

def connect_to_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rideshare.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
    db.app = app
    db.init_app(app)


def sha(passwo):
    if len(passwo) != 40:
        return False
    try:
        sha1 = int(passwo,16)
    except ValueError:
        return False
    return True

@app.route('/api/v1/db/write',methods = ['POST'])
def write_to_db():
        op=request.get_json()["op"]
        if int(op)==1:  
                username = request.get_json()["username"]
                password = request.get_json()["password"]

                add_user = User(username=username,password=password)
                db.session.add(add_user)
                db.session.commit()
                s={}
                res=User.query.filter_by(username=username).first()
                if res == None:
                        return "No"
                s["username"]=res.username
                return jsonify(s)
        if int(op)==2:
                created_by = request.get_json()["created_by"]
                timestamp = request.get_json()["timestamp"]
                source = request.get_json()["source"]
                destination = request.get_json()["destination"]
                add_ride = Ride(created_by=created_by,timestamp=timestamp,source=source,destination=destina$
                db.session.add(add_ride)
                db.session.commit()
                s={}
                res=Ride.query.filter_by(created_by=created_by).first()
                if res == None:
                        return "No"
                s["created_by"]=res.created_by
                return jsonify(s)

        if int(op)==3:
                username = request.get_json()['username']
                db.delete(username)
                db.session.commit()
        if int(op)==4:
                delete_ride.delete()
                delete_ride.session.commit()
        if int(op)==5:
                ride_id = request.get_json()["ride_id"]
                new_user_ride = JoinRide(ride_id=ride_id,username=username)
                db.session.add(new_user_ride)
                db.session.commit()
                s={}
                res=JoinRide.query.filter_by(username=username).first()
                if res == None:
                        return "No"
                s["username"]=res.username
                return jsonify(s)


@app.route('/api/v1/db/read',methods = ['POST'])
def read_to_db():
        rop=request.get_json()['rop']
        if int(rop)==1:
                username = request.get_json()["username"]
                return db.session.query(User).filter(User.username==username).all()
        if int(rop)==2:
                user_in_db=User.query.all()
                d=[]
                for i in user_in_db:
                        d.append(i.username)
                return jsonify(d)


@app.route('/api/v1/users', methods = ['PUT'])
def new_user():
        if (request.method=='PUT'):
                username=request.get_json()["username"]
                password=request.get_json()["password"]
                #user_in_db = db.session.query(User).filter(User.username==username).all()
                rquery = {"rop":1,"username":username}
                user = requests.post('http://localhost:80/api/v1/db/read',json=rquery)

                if not user:
                        check = sha(password)
                        if check:

                                query={"op":1,"username":username,"password":password}
                                user = requests.post('http://localhost:80/api/v1/db/write',json=query)
                                counter.value+=1
                                return jsonify({}),201

                        else:
                                return jsonify({}),400
                else:
                        return jsonify({}),400
        else:
                return jsonify({}),405

@app.route('/api/v1/db/clear',methods=["POST"])
def clear_db():
        user_in_db=db.session.query(User)
        user_in_db.delete()
        user_in_db.session.commit()
        counter.value+=1
        return jsonify({}),200

@app.route('/api/v1/users/<username>', methods=['DELETE'])
def del_user(username):
        user_in_db = db.session.query(User).filter(User.username==username)
        if str(user_in_db.first()) == username:
                user_in_db.delete()
                user_in_db.session.commit()
                counter.value+=1
                return jsonify({}),200
        else:
                return jsonify({}),400

@app.route('/api/v1/users', methods=['GET'])
def list_user():
        rquery = {"rop":2}
        user = requests.post('http://localhost:80/api/v1/db/read',json=rquery)
        if user.text==None:
                return jsonify(""),204
        else:
                res = json.loads(user.text)
                counter.value+=1
                return jsonify(res)
        return {},200

@app.route('/api/v1/_count',methods=['GET'])
def http_count():
        if(request.method=='GET'):
                with counter.get_lock():
                       L=[counter.value]
                return jsonify(L)




if __name__ == "__main__":

    #from server import app
    connect_to_db(app)
    db.create_all()
    print("connected to db")
    
    app.debug=True
    app.run(host='0.0.0.0',port=80)

# with counter.get_lock():
#       counter.value+=1






