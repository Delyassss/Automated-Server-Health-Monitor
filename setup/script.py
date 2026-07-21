import sys
import requests
import psutil
import time
import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import time

def print_sep():
	print("_" * 100 + '\n')
def print_time() :
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def docker_logs_header(logs) :
	print(f"====================================================\n{print_time()}\nRunning Containers\n====================================================", file=logs)   

load_dotenv()  # Load variables from .env file into the environment
to_gb = 1024 ** 3
discord__url = os.getenv('dis_url')
discord__token = os.getenv('dis_token')
headers = {"Autorisation " : discord__token}
last_alert = 0

def get_seconds() :
	seconds = time.time_ns() // 1_000_0000_000
	return seconds
	
def sys_usage(sys_cnf) :
		
	print_sep()
	print(f"TIME : [ {print_time()} ]\n")

# CPU
	cpu_usage = psutil.cpu_percent(interval=1)

	print(f"CPU USAGE : {cpu_usage}%")
	max = sys_cnf.get("cpu_limit", 90.0)
	print_sep()
	if cpu_usage > float(max) :
		print("[WARNING]: CPU usage is high")

# RAM

	RAM = psutil.virtual_memory()
	ram_total = RAM.total / to_gb
	ram_used = RAM.percent
	ram_available = RAM.available / to_gb

	print(f"TOTAL RAM : {ram_total:.2f} gb    |    RAM USAGE : {ram_used}%    |    RAM AVAILABLE : {ram_available:.2f} gb")
	max = sys_cnf.get("ram_limit", 85)
	print_sep()
	if ram_used > float(max) :
		print("[WARNING]: RAM usage is high")
#DISK
	DISK = psutil.disk_usage('/')
	ds_total = DISK.total / to_gb
	ds_used = DISK.percent
	ds_available = DISK.free / to_gb
	print(f"TOTAL DISK: {ds_total:.2f} gb    |    DISK USAGE : {ds_used}%    |    DISK AVAILABLE : {ds_available:.2f} gb")
	print_sep()
	max = sys_cnf.get("disk_limit" , 90)
	if ds_used > float(max) :
		print("[WARNING]: DISK usage is high")

def get_docker_status(logs) -> bool :

	try :
		ps = subprocess.run(['docker' , "info"], capture_output=True, text=True, check=True, timeout=10)
		docker_logs_header(logs)
		logs.write(ps.stdout)
		logs.write(ps.stderr)
		return True

	except subprocess.CalledProcessError:
			print("Error: Docker is not installed or not running.")
			docker_logs_header(logs)
			logs.write(f"FAILURE: Docker daemon error\n{e.stderr}\n")
			return False
	except FileNotFoundError :
			print("✗ Error: Docker CLI not found. Is Docker installed?")
			docker_logs_header(logs)
			return False
	except subprocess.TimeoutExpired : 
			print("✗ Error: Docker daemon is unresponsive (timeout).")
			docker_logs_header(logs)
			logs.write("FAILURE: Docker daemon timeout\n{e.stderr}")
			return False
	


def write_logs(file, what_to_write) :
		docker_logs_header(file)
		file.write(what_to_write)








def docker_monitoring(logs, data1, previous) :
	# docker info ...
	if get_docker_status(logs) == False :
		return
	
	# docker ps
	try :
		ps = subprocess.run(["docker" , "ps" , "-a" , "--format", "{{.Names}} | {{.Status}}"], capture_output=True, text=True, check=True)
		if not ps.stdout.strip() :
			raise ValueError("[Error] probably there is no data ! check if you have at least one container")
		docker_logs_header(sys.stdout)
		print(ps.stdout) 
		# i need to store the running container
		lines = ps.stdout.split('\n') # you should remove the  []  cuz it will create a nested list { [1 , 2 ,3] }
		for line in lines :
			if not line.strip() :
				continue 
			pipe = line.split('|') # Returns a flat list: ['key', 'value'] or ['key']
			if len(pipe) == 2 :
				data1[pipe[0].strip()] = { "state" : pipe[1],
							  				"last_alert" : get_seconds()
										}
			else :
				data1[pipe[0].strip()] =  {}

		# search the stopped container 
		for k , v in data1.items():
				
				current_state = v.get("state", "")

				if not previous :
					if "Exited" in current_state:
						print(f"[ALERT] : {k} has stopped!")
						send_discord_alert(k, v, "ALERT")
				else :
					if k not in previous :
						if "Exited" in current_state :
							print(f"[ALERT] : {k} has stopped (newly detected)!")
							send_discord_alert(k, v, "ALERT")
						elif "Up" in current_state:
							print(f"[SUCCESS] : {k} is UP (newly detected)!")
							send_discord_alert(k, v, "SUCCESS")
						continue
				
					if current_state != previous[k].get('state', "") :
						if "Exited" in current_state :
							print(f"[ALERT] : {k} has stopped!")
							send_discord_alert(k, current_state, "ALERT")
						elif "Up" in current_state :
							print(f"[SUCCESS] : {k} is UP!")
							send_discord_alert(k, current_state, "SUCCESS")
						else :
							print(f"[WARNING] : {k} -> { current_state }")
							send_discord_alert(k, current_state, "WARNING")

		previous = data1
		write_logs(logs, ps.stdout)
		write_logs(logs, ps.stderr)



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
		response = requests.post(discord__url, message, timeout=2, headers=headers);

	except requests.exceptions.Timeout :
			print("[Request Failed] timed out !")
	except requests.exceptions.RequestException as e :
			print("Request Failed : " , e )


def monitoring(config_dic, logs, data1, previous) :
		sys_usage(config_dic)
		docker_monitoring(logs, data1, previous)
		time.sleep(4)
		os.system("clear")


with open("./setup/docker.logs", 'a') as logs:
	with open("./setup/usage.conf", 'r') as config :

		data1 = {}
		previous = {}
		config_dic = {}
		for line in config :
			# Strip whitespace (including newlines) from the line
			line = line.strip()
			if not line :
				continue
			equal = line.split('=')
			if (len(equal) == 2) :
				config_dic[equal[0].strip()] =  equal[1].strip()

		if "--ci" in sys.argv :
			for i in range(4) :
				monitoring(config_dic, logs , data1, previous)
		else :
			while True :
				monitoring(config_dic, logs , data1, previous)
