import hashlib
import requests
import re
import json
from collections import defaultdict
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import pika
import json
import sqlalchemy as sql
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from random import randint
import ast

engine = sql.create_engine('sqlite:///database/RideShare.db', echo=True)
meta = sql.MetaData()
user_details = Table('UserDetails', meta, 
	Column('username', String, primary_key=True),
	Column('password', String),
	)
ride_details = Table('RideDetails', meta, 
	Column('ride_id', Integer, primary_key=True),
	Column('created_by', String),
	Column('timestamp', String),
	Column('source', String),
	Column('destination', String),
	)
join_ride = Table('JoinRide', meta,
	Column('join_id', Integer, primary_key=True),
	Column('ride_id', Integer),
	Column('created_by', String),
	)
count = Table('Count', meta,
	Column('count_id', Integer, primary_key=True),
	)

meta.create_all(engine)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rmq'))


def responseQueueFill(body,ch,properties,method):
	json_body = json.dumps(body)
	ch.basic_ack(delivery_tag=method.delivery_tag)
	ch.basic_publish(exchange="", routing_key='responseQ',properties=pika.BasicProperties(correlation_id = properties.correlation_id),body=json_body)

def syncQfill(ch,properties,body):
	ch.basic_publish(exchange="", routing_key='syncQ',body = body)
	



def callback2(ch, method, props, body):
    body = body.decode("utf-8").replace("'", '"')
    queryVal = ast.literal_eval(body)
    response = write_db(queryVal)
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel = connection.channel()

def write_db(queryVal):
		op = queryVal['op']
		columns = queryVal['column'] 
		table = queryVal['table']
		if op == "add":	
			values = queryVal['add']
			conn = engine.connect()
			query = "INSERT INTO " + table + "("
			for i in columns:
				query += i + ","
			query = query[:-1] + ") VALUES("
			for i in values:
				if type(i) == str:
					query += "'" + i + "',"
				elif type(i) == int:
					query += str(i) + ","
				else:
					print("UNSUPPORTED DATA-TYPE")
					exit(0)
			query = query[:-1] + ")"
			conn.execute(query)
			q = str(query)
			syncq_send(q)
			response = "DONE"

		elif op == "delete":
			condition = queryVal['cond']
			conn = engine.connect()
			query = "DELETE FROM "+ table + " WHERE " + ",".condition
			# print(query)
			conn.execute(query)
			q = str(query)
			syncq_send(q)

			response = "DONE"
		elif op == "delete_all":
			conn = engine.connect()
			query = "DELETE FROM "+ table
			# print(query)
			conn.execute(query)
			q = str(query)
			syncq_send(q)

			response = "DONE"
		
		else:
			response = "UNKNOWN action"
	
		return response



channel.basic_consume(on_message_callback = callback2, queue = 'syncQ',auto_ack = True)
print(' [*] Waiting for -----WRITE---- messages. To exit press CTRL+C')
channel.start_consuming()

if __name__ == '__main__':
	
	app.debug=True
	app.run(host="0.0.0.0", debug = True)
