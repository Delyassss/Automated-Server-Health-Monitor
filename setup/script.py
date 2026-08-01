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

def print_sep():
    # Gets current terminal width, defaults to 80 if unknown
		try :
			width = os.get_terminal_size().columns
		except Exception :
			width = 80
		print(f"\n{'=' * width}\n")

def print_time() :
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def docker_logs_header(logs) :
	print(f"====================================================\n[{print_time()}] 	[Containers -a]\n====================================================", file=logs)   
def header(where) :
	print("\n" + "="*40, file=where)
	print("CONTAINER MONITOR STARTED" , file=where)
	print("="*40 + "\n" , file=where)
def print_nested(data , redir , indent = 0) :
	for k , v in data.items() : 
		
		print(" " * indent + str(k), end="" , file=redir)
		if isinstance(v, dict) :
			print(file=redir);
			print_nested(v, redir , indent = indent + 1)
		else :
			print(f": {v}" , file = redir)


load_dotenv()  # Load variables from .env file into the environment
to_gb = 1024 ** 3
discord__url = os.getenv('dis_url')
discord__token = os.getenv('dis_token')
headers = {"Autorisation " : discord__token}
last_alert = 0

def get_seconds() :
	seconds = time.time_ns() // 1_000_0000_000 # It removes the fractional part of the division.
	return seconds
	
def sys_usage(system_dict, sys_cnf) :
		
	print_sep()
	print(f"TIME : [ {print_time()} ]\n")

# CPU
	cpu_usage = psutil.cpu_percent(interval=1)

	print(f"CPU USAGE : {cpu_usage}%")
	max = sys_cnf.get("cpu_limit", 90.0)
	print_sep()
	if cpu_usage > float(max) :
		print("[WARNING]: CPU usage is high")
	system_dict["CPU"] =	{"usage ": cpu_usage}
# RAM

	RAM = psutil.virtual_memory()
	ram_total = RAM.total / to_gb
	ram_used = RAM.percent
	ram_available = RAM.available / to_gb

	print(f"TOTAL RAM : {ram_total:.2f} GB    |    RAM USAGE : {ram_used}%    |    RAM AVAILABLE : {ram_available:.2f} GB")
	max = sys_cnf.get("ram_limit", 85)
	print_sep()
	if ram_used > float(max) :
		print("[WARNING]: RAM usage is high")
	system_dict["RAM"] =	{"TOTAL" : f"{ram_total:.2f} GB",
					   		 "USED" : f"{ram_used}%",
							 "AVAILABLE" : f"{ram_available:.2f} GB"
							}
#DISK
	DISK = psutil.disk_usage('/')
	ds_total = DISK.total / to_gb
	ds_used = DISK.percent
	ds_available = DISK.free / to_gb
	print(f"TOTAL DISK: {ds_total:.2f} GB    |    DISK USAGE : {ds_used}%    |    DISK AVAILABLE : {ds_available:.2f} GB")
	print_sep()
	max = sys_cnf.get("disk_limit" , 90)
	if ds_used > float(max) :
		print("[WARNING]: DISK usage is high")
	system_dict["DISK"] =	{"TOTAL" : f"{ds_total:.2f} GB",
							 "USED"  : f"{ds_used}%" ,
							 "AVAILABLE" : f"{ds_available:.2f} GB"
							}

def get_docker_status(logs) -> bool :

	try :
		ps = subprocess.run(['docker' , "info" , "--format" , "{{json .}}"], capture_output=True, text=True, check=True, timeout=10)
		in_json = json.loads(ps.stdout)
		print(
    		f"\n{'='*30}\n"
    		f"DOCKER SYSTEM STATUS\n"
    		f"{'='*30}\n"
    		f"Server Version: {in_json.get('ServerVersion', 'N/A')}\n"
    		f"Running Containers: {in_json.get('ContainersRunning', 0)}\n"
    		f"Paused Containers: {in_json.get('ContainersPaused', 0)}\n"
    		f"Stopped Containers: {in_json.get('ContainersStopped', 0)}\n"
    		f"{'='*30}\n" , file=logs
			)
		if  ps.stderr : 
			logs.write(f"[ERROR] {ps.stderr}")
		return True

	except subprocess.CalledProcessError:
			print("Error: Docker is not installed or not running.")
			logs.write(f"FAILURE: Docker daemon error\n{e.stderr}\n")
			return False
	except FileNotFoundError :
			print("✗ Error: Docker CLI not found. Is Docker installed?")
			return False
	except subprocess.TimeoutExpired : 
			print("✗ Error: Docker daemon is unresponsive (timeout).")
			logs.write("FAILURE: Docker daemon timeout\n{e.stderr}")
			return False
	


def write_docker_logs(file, what_to_write) :
		docker_logs_header(file)
		if (isinstance(what_to_write, dict)) :
			print_nested(what_to_write, file)
		else :
			file.write(what_to_write)








def docker_monitoring(logs, docker_dict, docker_previous , alerts) :
	# docker info ...
	if get_docker_status(logs) == False :
		return
	
	# docker ps
	try :
		ps = subprocess.run(["docker" , "ps" , "-a" , "--format", "{{.Names}} | {{.State}}"], capture_output=True, text=True, check=True)
		if not ps.stdout.strip() :
			raise ValueError("[Error] probably there is no data ! check if you have at least one container")
		username = getpass.getuser()
		docker_logs_header(sys.stdout)
		print(ps.stdout) 
		# i need to store the running container
		lines = ps.stdout.split('\n') # you should remove the  []  cuz it will create a nested list { [1 , 2 ,3] }
		for line in lines :
			if not line.strip() :
				continue 
			pipe = line.split('|') # Returns a flat list: ['key', 'value'] or ['key']
			if len(pipe) == 2 :
				docker_dict[pipe[0].strip()] = { "State" : pipe[1],
							  				"Last_alert" : print_time() ,
											  "Host" 	 : username
										}
			else :
				docker_dict[pipe[0].strip()] =  {}

		# search the stopped container 
		for k , v in docker_dict.items():
				
				current_state = v.get("state", "")

				if not docker_previous :
					print("HAHAHAH EMPTY docker_PREVIOUS")
					if "exited" in current_state:
						print(f"[ALERT] : {k} has stopped!")
						send_discord_alert(k, current_state, "ALERT")
						write_alerts_logs(k, current_state, "ALERT", alerts)
				else :
					if k not in docker_previous :
						if "exited" in current_state :
							print(f"[ALERT] : {k} has stopped (newly detected)!")
							send_discord_alert(k, current_state, "ALERT")
							write_alerts_logs(k, current_state, "ALERT", alerts)
						elif "running" in current_state:
							print(f"[SUCCESS] : {k} is UP (newly detected)!")
							send_discord_alert(k, current_state, "SUCCESS")
							write_alerts_logs(k, current_state, "SUCCESS", alerts)
						continue 
				
					if current_state != docker_previous[k].get('state', "") :
						if "exited" in current_state :
							print(f"[ALERT] : {k} has stopped!")
							send_discord_alert(k, current_state, "ALERT")
							write_alerts_logs(k, current_state, "ALERT", alerts)
						elif "running" in current_state :
							print(f"[SUCCESS] : {k} is UP!")
							send_discord_alert(k, current_state, "SUCCESS")
							write_alerts_logs(k, current_state, "SUCCESS", alerts)
						else :
							print(f"[WARNING] : {k} -> { current_state }")
							send_discord_alert(k, current_state, "WARNING")
							write_alerts_logs(k, current_state, "WARNING", alerts)


		#	docker_previous = docker_dict.copy() # Using docker_previous = docker_dict will not work correctly because it creates a reference, not a copy.
		#	but still won't work , because the = create a local docker_previous .
		# 	THE CORRECT: Modifies the actual dictionary object passed in
		docker_previous.clear()
		docker_previous.update(docker_dict)
		write_docker_logs(logs, docker_dict)
		if ps.stderr :
			write_docker_logs(logs, ps.stderr)



	except subprocess.CalledProcessError:
			print("Error: docker ps failed, check docker.logs !")
			return
	except FileNotFoundError :
			print("Error: File not found !")
			return
	except Exception as e :
			print(e)
			return 

def send_discord_alert(key, value, type) :
	try :
		print("[POST REQUEST] ...")
		message = f"[{type}] {print_time()} 🚨 {key} : {value}"
		in_json = {'content' : message}
		response = requests.post(discord__url, in_json, timeout=2, headers=headers);
		print(f"[REQUEST STATUS]   {response.status_code}")
		if response.text :
			print(f"[REQUEST RESPONSE] {response.text} ")

	except requests.exceptions.Timeout :
			print("[Request Failed] timed out !")
	except requests.exceptions.RequestException as e :
			print("Request Failed : " , e )

def write_alerts_logs(key, value, type, alerts) :
	message = f"[{type}] {print_time()} 🚨 {key} : {value}" 
	print(message , file=alerts)
	print_sep()
	

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
