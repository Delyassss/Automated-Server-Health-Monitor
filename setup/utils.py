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
import requests





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
			print(file=redir)
			print_nested(v, redir , indent = indent + 1)
		else :
			print(f": {v}" , file = redir)


load_dotenv()  # Load variables from .env file into the environment
to_gb = 1024 ** 3
discord__url = os.getenv('dis_url')
discord__token = os.getenv('dis_token')
headers = {"Autorisation " : discord__token}



def get_seconds() :
	seconds = time.time_ns() // 1_000_0000_000 # It removes the fractional part of the division.
	return seconds

def write_alerts_logs(key, value, type, alerts) :
	message = f"[{type}] {print_time()} 🚨 {key} : {value}" 
	print(message , file=alerts)
	print_sep()