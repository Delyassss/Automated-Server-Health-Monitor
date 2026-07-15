import psutil
import time
import os
import subprocess
from datetime import datetime

def print_sep():
	print("_" * 100 + '\n')
def print_time() :
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def docker_logs_header(logs) :
	print(f"====================================================\n{print_time()}\nRunning Containers\n====================================================", file=logs)   


to_gb = 1024 ** 3


def sys_usage() :
	print_sep()
	print(f"TIME : [ {print_time()} ]\n")

# CPU
	cpu_usage = psutil.cpu_percent(interval=1)

	print(f"CPU USAGE : {cpu_usage}%")
	print_sep()

# RAM

	RAM = psutil.virtual_memory()
	ram_total = RAM.total / to_gb
	ram_used = RAM.percent
	ram_available = RAM.available / to_gb

	print(f"TOTAL RAM : {ram_total:.2f} gb    |    RAM USAGE : {ram_used}%    |    RAM AVAILABLE : {ram_available:.2f} gb")
	print_sep()
#CPU

	DISK = psutil.disk_usage('/')
	ds_total = DISK.total / to_gb
	ds_used = DISK.percent
	ds_available = DISK.free / to_gb
	print(f"TOTAL DISK: {ds_total:.2f} gb    |    DISK USAGE : {ds_used}%    |    DISK AVAILABLE : {ds_available:.2f} gb")
	print_sep()


def docker_monitoring(logs) :

# Docker Services
	try :
		ps = subprocess.run(["docker", "--version"], capture_output=True, text=True, check=True)
		print(ps.stdout)
		docker_logs_header(logs)
		logs.write(ps.stdout)
		logs.write(ps.stderr)

	except subprocess.CalledProcessError:
			print("Error: Docker is not installed or not running.")
			return
	
	#running
	try :
		ps = subprocess.run(["docker" , "ps"], capture_output=True, text=True, check=True)
		print(ps.stdout)
		docker_logs_header(logs)
		logs.write(ps.stdout)
		logs.write(ps.stderr)
	#stopped
		ps = subprocess.run(["docker" ,  "ps" ,  "-a" , "--filter" , "status=exited"], capture_output=True ,  text=True , check=True)
		print(ps.stdout)
		if "Exited" in ps.stdout :
				print("A container has stopped!")
		docker_logs_header(logs)
		logs.write(ps.stdout)
		logs.write(ps.stderr)
	except subprocess.CalledProcessError:
			print("Error: docker ps failed, check docker.logs !")
			return
	except FileNotFoundError :
			print("Error: File not found !")
			return





with open("docker.logs", 'a') as logs:

	while True :
		sys_usage()
		docker_monitoring(logs)
		time.sleep(4)
		os.system("clear")

































	time.sleep(4)
	os.system("clear")