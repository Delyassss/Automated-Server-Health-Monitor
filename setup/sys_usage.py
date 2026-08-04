from utils import *



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
	system_dict["CPU"] =	{"USED": f"{cpu_usage}%"}
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