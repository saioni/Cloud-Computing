from flask_sqlalchemy import SQLAlchemy
from flask import Flask,request,session,jsonify,abort
import json
import sqlite3
from sqlalchemy import Column, String, Integer
from datetime import datetime as dt
from multiprocessing import Value

import requests
counter=Value('i',0)
app = Flask(__name__)


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
                (self.username,self.ride_id)

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
#@app.route('/api/v1/db/read',methods = ['POST'])
#def read_to_db():
#       if int(rop)==1:
#               username = request.get_json()["username"]
#               user_in_db = db.session.query(User).filter(User.username==username).all()


@app.route('/api/v1/rides', methods = ['POST'])
def create_ride():
        if (request.method == 'POST'):
                created_by = request.get_json()["created_by"]
                timestamp = request.get_json()["timestamp"]
                source = request.get_json()["source"]
                destination = request.get_json()["destination"]
                #user_in_db = db.session.query(User).filter(User.username==created_by)
                user_exist = requests.get('http://my-load-balancer-621305378.us-east-1.elb.amazonaws.com/ap$
                if not user_exist:
                                print('cant reach elb')
                                return {}, 400
                res = json.loads(user_exist.text)
                if created_by in res:
                        query = {"op":2,"created_by":created_by,"timestamp":timestamp,"source":source,"dest$
                        ride = requests.post('http://localhost:80/api/v1/db/write',json=query)
                        counter.value+=1
                        return jsonify({}),201
                else:
                        print("username doesn't exist")
                        return jsonify({}),400
    
@app.route('/api/v1/rides/<int:ride_id>', methods=['DELETE'])
def del_ride(ride_id):
        if(request.method=='DELETE'):
                delete_ride = db.session.query(Ride).filter(Ride.ride_id==ride_id)
                query = {"op":4}
                del_user = requests.post('http://localhost:80/api/v1/db/write',json={"query":query})
                counter.value+=1
                return jsonify({}),200
        else:
                return jsonify({}),400

@app.route('/api/v1/rides/<int:ride_id>', methods=['GET'])
def details_ride(ride_id):
        if(request.method=='GET'):

                ride_details = db.session.query(Ride).filter_by(ride_id=ride_id).first()
                s={}
                s["created_by"] = ride_details.created_by
                s["timestamp"] = ride_details.timestamp
                s["source"] = ride_details.source
                s["destination"] = ride_details.destination
                counter.value+=1
                return jsonify(s),200
        else:
                return jsonify({}),405

@app.route('/api/v1/db/clear',methods=["POST"])
def clear_db():
        user_in_db=db.session.query(Ride)
        user_in_db.delete()
        user_in_db.session.commit()
        counter.value+=1
        return jsonify({}),200

@app.route('/api/v1/rides',methods=['GET'])
def upcoming_ride():
        if (request.method == 'GET'):
                source = request.args['source']
                destination = request.args['destination']
                sd_in_db = db.session.query(Ride).filter(Ride.source==source and Ride.destination==destinat$
                if not sd_in_db:
                        abort(400)
                else:

                        d = []

                        for i in sd_in_db:
                                dt_time = dt.strptime(i.timestamp,"%d-%m-%Y:%S-%M-%H")
                                if dt_time > dt.now():
                                        d.append({"ride_id":i.ride_id,"created_by":i.created_by,"timestamp"$
                        counter.value+=1
                        return jsonify(d)

        else:
                return jsonify({}),405



@app.route('/api/v1/rides/<int:ride_id>',methods = ['POST'])
def join_ride(ride_id):
        if (request.method=='POST'):
                #ride_id = Ride.query.get(ride_id)
                rideid_in_db = db.session.query(Ride).filter(Ride.ride_id==ride_id)
                username = request.get_json()["username"]
                user_in_db = db.session.query(User).filter(User.username==username).all()
                if not user_in_db and not rideid_in_db:
                        abort(400)
                else:
                        query={"op":5,"ride_id":ride_id,"username":username}
                        join_ride = requests.post('http://localhost:80/api/v1/db/write',json=query)
                        s={}
                        res=JoinRide.query.filter_by(username=username).first()

                        if res == None:
                                return "No"
                        s["username"]=res.username
                        counter.value+=1
                        return jsonify(s)
        else:
                return jsonify({}),405

@app.route('/api/v1/rides/count',methods=['GET'])
def rides_count():
        if (request.method=='GET'):
                rides_in_db=db.session.query(Ride).all()
                count = len(rides_in_db)
                counter.value+=1
                return jsonify([count]),200
        else:
                return jsonify({}),405

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






