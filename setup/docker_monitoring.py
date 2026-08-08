from utils import *
from discord import *





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
	

def docker_monitoring(logs, docker_dict, docker_previous , alerts) :
	# docker info ...
	if get_docker_status(logs) == False :
		return
	
	# docker ps
	try :
		ps = subprocess.run(["docker" , "ps" , "-a" , "--format", "{{.Names}} | {{.State}}"], capture_output=True, text=True, check=True)
		if not ps.stdout.strip() :
			raise ValueError("[Error] probably there is no data ! check if you have at least one container")
		docker_dict.clear()
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
				docker_dict[pipe[0].strip()] = { "State" : pipe[1].strip(),
							  				"Last_alert" : print_time() ,
											  "Host" 	 : username
										}
			else :
				docker_dict[pipe[0].strip()] =  {}

		# search the stopped container 
		for k , v in docker_dict.items():
				
				current_state = v.get("State", "")

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
				
					if current_state != docker_previous[k].get('State', "") :
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

def write_docker_logs(file, what_to_write) :
		docker_logs_header(file)
		if (isinstance(what_to_write, dict)) :
			print_nested(what_to_write, file)
		else :
			file.write(what_to_write)