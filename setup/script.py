import psutil
import time


psutil.cpu_percent(interval=None) # init 0.0

while True :

	cpu_usage = psutil.cpu_percent(interval=None)

	print(f"CPU USAGE : {cpu_usage}%")

# RAM
	to_gb = 1024 ** 3

	RAM = psutil.virtual_memory()
	ram_total = RAM.total / to_gb
	ram_used = RAM.percent
	ram_available = RAM.available / to_gb


	print(f"TOTAL RAM : {ram_total:.2f}%    |    RAM USAGE : {ram_used}%    |    RAM AVAILABLE : {ram_available:.2f}%")
	

	time.sleep(3)