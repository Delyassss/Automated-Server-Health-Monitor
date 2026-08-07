import sys
import requests
import psutil
import time
import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import time
import json
import getpass
import threading
from flask import Flask, request, render_template
from utils import *
from docker_monitoring import *
from discord import *
from sys_usage import *


lock = threading.Lock()

def monitoring(system_dict, config_dic, logs, docker_dict, docker_previous, alerts) :
		sys_usage(system_dict, config_dic)
		docker_monitoring(logs, docker_dict, docker_previous, alerts)
		time.sleep(4)
		running=0
		stopped=0
		os.system("clear")

def thread_monitor() :
		if "--ci" in sys.argv :
			for i in range(4):
				try:
					monitoring(system_dict, config_dic, logs, docker_dict, docker_previous, alerts)
				except Exception as e:
					print(f"Monitoring failed on iteration {i}: {e}")
					sys.exit(1)
		else :
			while True :
				try :
					monitoring(system_dict, config_dic, logs , docker_dict, docker_previous, alerts)
				except Exception as e :
					print(f"Monitoring failed : {e}")
					sys.exit(1)


def flask_server() :
	app = Flask(__name__, template_folder="design")


	@app.route('/', methods=['GET'])
	def info() :
		running = 0
		stopped = 0
		for container in docker_dict.values():
			if "running" in container.get("State", "").lower():
				running += 1
			else:
				stopped += 1

		if request.method == 'GET' :
			return render_template('index.html', system_dict=system_dict, docker_dict=docker_dict, running=running, stopped=stopped, time=print_time())
		return render_template('index.html', system_dict=system_dict, docker_dict=docker_dict, running=running, stopped=stopped, time=print_time())
	
	if (1024 < Flask_port < 65536) :
		app.run(host='0.0.0.0', port=(Flask_port), debug=True, use_reloader=False)
	else :
		app.run(host='0.0.0.0', debug=True , use_reloader=False)



	

with open("./setup/logs/docker.log", 'a') as logs:
	with open("./setup/conf/usage.conf", 'r') as config :
		with open("./setup/logs/alerts.log", 'a') as  alerts :
			docker_dict = {} # For Docker
			docker_previous = {}
			config_dic = {}
			system_dict = {}
			for line in config :
				# Strip whitespace (including newlines) from the line
				line = line.strip()
				if not line :
					continue
				equal = line.split('=')
				if (len(equal) == 2) :
					config_dic[equal[0].strip()] =  equal[1].strip()
			header(sys.stdout)
			header(logs)
			header(alerts)
			threads = []

			t = threading.Thread(target=thread_monitor)
			threads.append(t)
			t = threading.Thread(target=flask_server)
			threads.append(t)

			for t in threads :
				t.start()
			for t in threads :
				t.join()