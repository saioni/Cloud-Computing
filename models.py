from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer,autoincrement=True, primary_key = True)
    username = db.Column(db.String(32),index=True)
    password = db.Column(db.String(40))

    def __repr__(self):
        return self.username


class Ride(db.Model):
    __tablename__ = "rides"
    ride_id = db.Column(db.Integer,autoincrement=True, primary_key = True)
    created_by = db.Column(db.String(32),index=True)
    timestamp = db.Column(db.DateTime)
    source = db.Column(db.String(40))
    destination = db.Column(db.String(40))

    def __repr__(self):
        return (self.created_by,
                self.timepstamp,
                self.source,
                self.destination)



class upcoming_rides(db.Model):
    __tablename__="upcoming_rides"
    ride_id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(32),index=True)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return (self.ride_id,
                self.username,
                self.timestamp)
    
    

class ride_details(db.Model):
    __tablename__ = "tripdetails"
    ride_id = db.column(db.Integer,ab.ForeignKey("rides.ride_id"),primary_key=True)
    created_by = db.Column(db.String,nullable=False)
    users = db.Column()
    timestamp = db.Column(db.DateTime)
    source = db.Column(db.String(40),index=True)
    destination = db.Column(db.String(40),index=True)

    def __repr__(self):


class join_exist(db.Model):
    __tablename__ = "existing_ride"
    id = db.Column(db.Integer,autoincrement=True,primary_key-True)
    username = db.Column(db.String(32),index=True)

    def __repr__(self):



        


def connect_to_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rideshare.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
    db.app = app
    db.init_app(app)


if __name__=="__main__":
    from server import app
    connect_to_db(app)
    db.create_all()
    print("connected to db")
    
