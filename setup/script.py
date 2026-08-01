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
from docker_monitoring import *
from sys_usage import *
from utils import *
from discord import *


def monitoring(system_dict, config_dic, logs, docker_dict, docker_previous, alerts) :
		sys_usage(system_dict, config_dic)
		docker_monitoring(logs, docker_dict, docker_previous, alerts)
		time.sleep(4)
		os.system("clear")


with open("./setup/docker.log", 'a') as logs:
	with open("./setup/usage.conf", 'r') as config :
		with open("./setup/alerts.log", 'a') as  alerts :
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

			if "--ci" in sys.argv :
				for i in range(4) :
					monitoring(system_dict, config_dic, logs , docker_dict, docker_previous, alerts)
			else :
				while True :
					monitoring(system_dict, config_dic, logs , docker_dict, docker_previous, alerts)
