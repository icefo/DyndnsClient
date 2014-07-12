#!/usr/bin/env python3
from urllib.request import Request, urlopen
from urllib.error import  URLError
from datetime import datetime
import base64, re, configparser, argparse, sys, os.path

Username = 'My Username'
Password = 'My Secure Password'
Host = 'www.ovh.com' # replace this with your dyndns' domain name 
Hostname = 'subdomain.domain.net'
Whatsmyip = 'http://checkip.dyndns.com/', 'http://wtfismyip.com/text'
User_Agent = "icefo's dyndns updater -- https://github.com/icefo/DyndnsClient" # or "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
Use_Https = True

Path_To_IpFile = "{}/".format(os.path.expanduser("~")) + '.DyndnsClientIpHistory'
IpFile = ''
myip = ''
http_mode = '' # ssl or not
credentials = '' # credentials for the ip update query
url_1 = '' # url for the ip update query
headers_1 = '' # User-Agent for Whatsmyip query
headers_2 = '' # headers for the ip update query
Date_now = str(datetime.now())


# This bloc of code is used to parse an eventual config file and check if you want to force the ip update
parser = argparse.ArgumentParser(description="A simple dyndns update client in python 3\nhttps://github.com/icefo/DyndnsClient for more infos")
parser.add_argument("-ptc", "--Path_To_ConfigFile", help="You can call this script with a config file so specify the path here")
parser.add_argument("-F", "--Force_Ip_Update", help="Force ip update", action="store_true")
args = parser.parse_args()
Path_To_ConfigFile = args.Path_To_ConfigFile

if args.Path_To_ConfigFile:
	config = configparser.RawConfigParser()
	config.optionxform = lambda option: option # option for case sensitive variable
	config.read(Path_To_ConfigFile)
	for key in config['Main']:
		globals()[key]  = config['Main'][key]


if Use_Https:
	http_mode = 'https://'
else:
	http_mode = 'http://'


# Function used to make HTTP requests
def HTTP_Client(url, headers):
	req = Request(url, None, headers)
	try:
		answer = urlopen(req)
	except URLError as e: # HTTP error
		if hasattr(e, 'code'):
			return("","",e.code,"")
		elif hasattr(e, 'reason'): # server unreachable 
			return("","","",e.reason)
	else:
		return(answer.read(),answer.info(),"","") # order : http contents, http server headers, http error, server unreachable


# Function used to analyse the answer of the function HTTP_Client in the "find the host's ip" bloc of code
def HTTP_Answer_Test(HTTP_Answer,server):
	if HTTP_Answer[0]:
		return(re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", str(HTTP_Answer[0]))[0])
	elif HTTP_Answer[2]:
		return('HTTP Error Code ' + str(HTTP_Answer[2]) + ' for ' + server + ' -- ' + Date_now)
	elif HTTP_Answer[3]:
		return('Server unreachable (DNS, no connection ?) ' + str(HTTP_Answer[3]) + ' for ' + server + ' -- ' + Date_now)


# find the host's ip
headers_1 = {'User-Agent': User_Agent}
for x in Whatsmyip:
	y = HTTP_Client(x, headers_1)
	if (y[0] and not HTTP_Answer_Test(y, x) == ""):
		myip = HTTP_Answer_Test(y, x)
		break
	else:
		print(HTTP_Answer_Test(y, x))
		if (x == Whatsmyip[-1]):
			raise ValueError("The script wasn't able to get a valid output from the given servers. It has therefore self-terminated" + ' -- ' + Date_now)


#check if the ip is still the same
if not os.path.isfile(Path_To_IpFile):
	with open(Path_To_IpFile, 'w') as f:
		f.write('0.0.0.0\n0.0.0.0\n0.0.0.0\n0.0.0.0\n0.0.0.0')

with open(Path_To_IpFile, 'r') as f:
	IpFile = f.read().split('\n')[-5:]

if (myip == IpFile[-1]):
	if args.Force_Ip_Update:
		print('You forced the', myip, 'ip update, this may raise an error')
	else:
		print('The ip', myip, 'hasn\'t changed since last check' + ' -- ' + Date_now)
		sys.exit(1)
else:
	IpFile.extend([myip])
	with open(Path_To_IpFile, 'w') as f:
		f.write('\n'.join(IpFile))


# Transform/format the credentials to make them conform to the HTTP Basic Auth standard
# The requests lib has probably a function to do that
credentials = Username + ':' + Password
credentials = base64.standard_b64encode(bytes(credentials, "utf8"))
credentials = 'Basic ' + str(credentials)[2:-1]


# Make url and headers for the update query
url_1 = http_mode + Host + '/nic/update?system=dyndns' + '&hostname=' + Hostname + '&myip=' + myip
headers_2 = {'Host': Host, 'Authorization': credentials, 'User-Agent': User_Agent}

# The ip update happend just under this comment
Update_Answer = HTTP_Client(url_1, headers_2)
if (re.findall("^b'good", str(Update_Answer[0]))):
	print("Hourra ! new ip is " + myip + ' -- ' + Date_now)
elif (re.findall("^b'nochg", str(Update_Answer[0]))):
	raise ValueError("The ip submitted to the server hasn't changed since last update\nThis shouldn't happen" + ' -- ' + Date_now)
elif Update_Answer[2]:
	if (Update_Answer[2] == 401):
		raise ValueError('Wrong credentials, HTTP error 401' + ' -- ' + Date_now)
	elif (Update_Answer[2] == 404):
		raise ValueError('Page Not Found, HTTP error 404, probably an error in the url_1 variable' + ' -- ' + Date_now)
	else:
		raise ValueError('HTTP Error Code ' + str(Update_Answer[2]) + ' for ' + url_1 + ' -- ' + Date_now)
elif Update_Answer[3]:
	raise ValueError('Server unreachable (DNS, no connection ?) ' + str(Update_Answer[3]) + ' for ' + url_1 + ' -- ' + Date_now)
else:
	raise ValueError("The script the script has encountered an unexpected error\nGood luck !\n" + str(Update_Answer[0] + '\n' + url_1) + ' -- ' + Date_now)
