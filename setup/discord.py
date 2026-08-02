from utils import *

def send_discord_alert(key, value, type) :
	try :
		print("[POST REQUEST] ...")
		message = f"[{type}] {print_time()} 🚨 {key} : {value}"
		in_json = {'content' : message}
		response = requests.post(discord__url, in_json, timeout=2, headers=headers)
		print(f"[REQUEST STATUS]   {response.status_code}")
		if response.text :
			print(f"[REQUEST RESPONSE] {response.text} ")

	except requests.exceptions.Timeout :
			print("[Request Failed] timed out !")
	except requests.exceptions.RequestException as e :
			print("Request Failed : " , e )