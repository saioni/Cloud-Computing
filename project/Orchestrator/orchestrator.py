import pika
import uuid
from flask import Flask, render_template, jsonify, request,abort
import docker
import os
import tarfile
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from random import randint
import atexit


zk = KazooClient(hosts='zoo:2181')

def zk_listener(state):
	if(state == KazooState.LOST):
		logging.warning("Zookeeper connection lost")
	elif(state == KazooState.SUSPENDED):
		logging.warning("Zookeeper connection suspended")
	else:
		logging.info("Zookeeper connected")

zk.add_listener(zk_listener)
zk.start()

if(zk.exists("/Workers")):
	zk.delete("/Workers", recursive=True)

@zk.ChildrenWatch("/Workers/",send_event = True)
def watch_children(children,event):
	print("Children are now: %s" % children)
	if(event == None):
		pass
	elif(event.type is DELETED):
		print("Slave deleted")



timer_start_flag = False
timer_started_flag = False
read_request_count = 0
containers_running = {}
pid_name_mapping = {}
 
containers_running_index = 0

client = docker.from_env()
client = docker.DockerClient(base_url='unix://var/run/docker.sock')
x_client = docker.APIClient(base_url='unix://var/run/docker.sock')

containers_running[containers_running_index] = client.containers.run(image="slave:latest", command =["python","slave.py"], \
detach=True,network = 'project_default',volumes = {'/home/saioni/Orchestrator/database':{'bind': '/code/sdb'}})
containers_running_index +=1
time.sleep(5)

client.containers.run(image="master:latest", command =["python","master.py"], \
detach=True,network = 'project_default')
time.sleep(5)

client.containers.run(image="shared_db:latest", command =["python","shared_db.py"], \
detach=True,network = 'project_default',volumes = {'/home/saioni/Orchestrator/database':{'bind': '/code/sdb'}})
time.sleep(5)


def trigger_timer():
	
	global timer_started_flag
	global timer_start_flag
	
	if(not (timer_started_flag) and (timer_start_flag)):
		timer_started_flag = True
		scale_timer()

def scale_timer():
	
	print('timer')
	global read_request_count
	global containers_running
	global pid_name_mapping
	global containers_running_index
	global client
	global x_client

	if(read_request_count == 0):
		no_of_slaves = 1
	elif(read_request_count%20 == 0):
		no_of_slaves = int(read_request_count/20)
	else:
		no_of_slaves = int(read_request_count/20) + 1
	if(len(containers_running.keys()) <= no_of_slaves):
		t = len(containers_running.keys())
		for i in range(t,no_of_slaves):
			
			containers_running[containers_running_index] = client.containers.run(image="slave:latest", command =["python","slave.py"], \
			detach=True,network = 'project_default',volumes = {'/home/saioni/Orchestrator/database':{'bind': '/code/sdb'}})
			time.sleep(5)
			
			Name = containers_running[containers_running_index].name
			
			Pid = x_client.inspect_container(Name)['State']['Pid']
			pid_name_mapping[containers_running_index] = {'Name':Name, 'Pid': Pid}
			containers_running_index +=1
	
	elif(len(containers_running.keys()) > no_of_slaves):
		while len(containers_running.keys()) > no_of_slaves:
			containers_list = list(containers_running.keys())
			if(len(containers_list) == 0):
				min_pid = -1
			else:
				min_pid = containers_list[0]
			for i in range(0,containers_running_index):
				if(i in containers_running.keys() and x_client.inspect_container(containers_running[i].name)['State']['Pid'] < x_client.inspect_container(containers_running[min_pid].name)\
				['State']['Pid'] ):
					min_pid = i
			
			if(min_pid is not -1):
				containers_running[min_pid].stop()
				containers_running[min_pid].remove()
				del containers_running[min_pid]
				del pid_name_mapping[min_pid]
	
	print(containers_running)
	
		
	read_request_count = 0
	timer = threading.Timer(120, scale_timer)
	timer.start()




class writeData(object):
    def __init__(self,type):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rmq',heartbeat = 0))
        self.channel = self.connection.channel()	
        
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue = result.method.queue
        self.channel.basic_publish(queue=self.queue, routing_key='', body=str(message))
        self.connection.close()

class MyRPC(object):

    def __init__(self, type):
        self.rpc_type = type
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rmq',heartbeat = 0))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, details):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key=self.rpc_type+'Q',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
		content_type = "application/json",
            ),
            body=str(details))
        while(self.response is None):
            self.connection.process_data_events()
        return (self.response)

write_rpc = MyRPC("write")
read_rpc = MyRPC("read")
app=Flask(__name__)


def dataReplication(name,dst,src):
    
    container = client.containers.get(name)
    os.chdir(os.path.dirname(src))
    srcname = os.path.basename(src)
    tar = tarfile.open(src + '.tar', mode='w')
    try:
        tar.add(srcname)
    finally:
        tar.close()

    data = open(src + '.tar', 'rb').read()
    container.put_archive(os.path.dirname(dst), data)

@app.route("/api/v1/db/write", methods=["POST"])
def write_deb():
    details = request.get_json()
    response = write_rpc.call(details)
    return response.decode("utf-8")   

@app.route("/api/v1/db/clear",methods=["POST"])
def clear_db():
    query1={"op":"delete_all","table":"UserDetails","column":'',"cond":''}
    requests.post('http://0.0.0.0:80/api/v1/db/write',json=query1)
    query2={"op":"delete_all","table":"RideDetails","column":'',"cond":''}
    requests.post('http://0.0.0.0:80/api/v1/db/write',json=query2)
    query3={"op":"delete_all","table":"JoinRide","column":'',"cond":''}
    requests.post('http://0.0.0.0:80/api/v1/db/write',json=query3)
    return {}

@app.route("/api/v1/db/read", methods=["POST"])
def read_deb():
    
   	global timer_start_flag 
	global read_request_count 
	timer_start_flag = True
	read_request_count +=1
	trigger_timer()
    details = request.get_json()
    response = read_rpc.call(details)
    return response.decode("utf-8")

@app.route("/api/v1/worker/list",methods=["GET"])
def list_worker():
	client = docker.from_env()
	pid_list = []
	for c in client.containers.list():
		if not (c.name =="rmq" or c.name =="orchestrator"):
			pid = c.top()['Processes'][0][1]
			pid_list.append(int(pid))
	pid_list.sort()
	return str(pid_list)

@app.route("/api/v1/crash/slave",methods=["POST"])
def crash():
	client = docker.from_env()
	pid_list = []
	c_list=[]
	for c in client.containers.list():
		if not (c.name =="rmq" or c.name =="orchestrator" or c.name=="master1"):
			pid = c.top()['Processes'][0][1]
			pid_list.append(pid)
			c_list.append(c)
	pid_list.sort()
	pid_to_kill = pid_list[-1]
	for c in c_list:
		if(c.top()['Processes'][0][1] == pid_to_kill):
			c.kill()
	return str(pid_to_kill)

@app.route("/api/v1/_count", methods=["GET"])
def getCount():
    f = open("myCount.txt", "r")
    count = f.read()
    f.close()
    return count

if __name__ == '__main__':	
	app.debug=True
	initCount()
	app.run(host="0.0.0.0", port = 80, use_reloader=False)
	
	
	
	
	
	
	
