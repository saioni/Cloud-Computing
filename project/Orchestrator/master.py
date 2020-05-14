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

channel2 = connection.channel()
channel2.exchange_declare(exchange='syncq', exchange_type='fanout')

def syncq_send(query_data):
	channel2.basic_publish(exchange='syncq', routing_key='', body=query_data)
	print(" sent ",query_data)

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


def read_db(queryVal):
	
		table = queryVal['table']
		columns = queryVal['column']
		condition = queryVal['cond']
		conn = engine.connect()
		query = "SELECT " + ",".join(columns) + " FROM " + table
		if condition:
			query += " WHERE " + ",".join(condition)
		res = conn.execute(query)
		res = list(res)
		for index, _ in enumerate(res):
			res[index] = tuple(res[index])
		return json.dumps(res)
	
def callback1(ch, method, properties, body):
	print("callback1 function working")
	
	statement = str(body)
	statement = statement.strip("b")
	statement = statement.strip("\'")
	statement = statement.strip("\"")
	statement = text(statement)
	result = db.engine.execute(statement.execution_options(autocommit = True))
	result = result.fetchall()
	res = []
	for i in result:
		res.append(dict(i))

	responseQueueFill(res,ch,properties)

	print(" [x] Received CallBack1 %r \n" % body)


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
channel.queue_declare(queue='writeQ')
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='writeQ', on_message_callback=callback2)

channel.start_consuming()
