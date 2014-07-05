#!/bin/env python3
from urllib.request import Request, urlopen
from urllib.error import  URLError
import base64, re, configparser, argparse, sys, os.path

Username = 'My Username'
Password = 'My Secure Password'
Host = 'www.ovh.com' # replace this with your dyndns' domain name 
Hostname = ['subdomain.domain.net']
Whatsmyip = 'http://checkip.dyndns.com/', 'http://wtfismyip.com/text'
User_Agent = "icefo's dyndns updater" # or "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
Use_Https = True
Path_To_IpFile = "{}/".format(os.path.expanduser("~")) + '.DyndnsClientIpHistory'

myip = ''
http_mode = '' # ssl or not
credentials = '' # credentials for the ip update query
url_1 = '' # url for the ip update query
headers_1 = '' # User-Agent for Whatsmyip query
headers_2 = '' # headers for the ip update query


parser = argparse.ArgumentParser(description="A simple dyndns update client in python 3\nhttps://github.com/icefo/DyndnsClient for more infos")
parser.add_argument("-ptc", "--Path_To_ConfigFile", help="You can call this script with a config file so specify the path here")
args = parser.parse_args()
Path_To_ConfigFile = args.Path_To_ConfigFile


if Path_To_ConfigFile:
	config = configparser.RawConfigParser()
	config.optionxform = lambda option: option # option for case sensitive variable
	config.read(Path_To_ConfigFile)
	for key in config['Main']:
		globals()[key]  = config['Main'][key]
	Whatsmyip = Whatsmyip.split(' , ') # make Tuple
	Hostname = Hostname.split(' , ')
	if (Use_Https.lower() == 'true'):
		Use_Https = True
	else:
		Use_Https = False


if Use_Https:
	http_mode = 'https://'
else:
	http_mode = 'http://'


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

def HTTP_Answer_Test(HTTP_Answer,server):
	if HTTP_Answer[0]:
		return(re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", str(HTTP_Answer[0]))[0])
	elif HTTP_Answer[2]:
		return('HTTP Error Code ' + str(HTTP_Answer[2]) + ' for ' + server)
	elif HTTP_Answer[3]:
		return('Server unreachable (DNS, no connection ?) ' + str(HTTP_Answer[3]) + ' for ' + server)


headers_1 = {'User-Agent': User_Agent}
for x in Whatsmyip: # find the host's ip
	y = HTTP_Client(x, headers_1)
	if (y[0] and not HTTP_Answer_Test(y, x) == ""):
		myip = HTTP_Answer_Test(y, x)
		break
	else:
		print(HTTP_Answer_Test(y, x))
		if (x == Whatsmyip[-1]):
			raise ValueError("The script wasn't able to get a valid output from the given servers. It has therefore self-terminated")

#myip = '8.8.8.8'

#check if the ip is still the same


if not os.path.isfile(Path_To_IpFile):
	with open(Path_To_IpFile, 'w') as f:
		f.write('0.0.0.0\n0.0.0.0\n0.0.0.0\n0.0.0.0\n0.0.0.0')

with open(Path_To_IpFile, 'r') as f:
	data = f.read().split('\n')[-5:]

if (myip == data[-1]):
	print('The ip', myip, 'hasn\'t changed since last check')
	sys.exit(1)
else:
	data.extend([myip])
	with open(Path_To_IpFile, 'w') as f:
		f.write('\n'.join(data))


credentials = Username + ':' + Password
credentials = base64.standard_b64encode(bytes(credentials, "utf8"))
credentials = 'Basic ' + str(credentials)[2:-1]

url_1 = http_mode + Host + '/nic/update?system=dyndns' + '&hostname=' + ','.join(Hostname) + '&myip=' + myip
headers_2 = {'Host': Host, 'Authorization': credentials, 'User-Agent': User_Agent}

# The ip update happend just under this comment
Update_Answer = HTTP_Client(url_1, headers_2)
if (re.findall("^b'good", str(Update_Answer[0]))):
	print("Hourra ! new ip is " + myip)
elif (re.findall("^b'nochg", str(Update_Answer[0]))):
	raise ValueError("The ip submitted to the server hasn't changed since last update\nThis shouldn't happen")
elif Update_Answer[2]:
	if (Update_Answer[2] == 401):
		raise ValueError('Wrong credentials, HTTP error 401')
	elif (Update_Answer[2] == 404):
		raise ValueError('Page Not Found, HTTP error 404, probably an error in the url_1 variable')
	else:
		raise ValueError('HTTP Error Code ' + str(Update_Answer[2]) + ' for ' + url_1)
elif Update_Answer[3]:
	raise ValueError('Server unreachable (DNS, no connection ?) ' + str(Update_Answer[3]) + ' for ' + url_1)
else:
	raise ValueError("The script the script has encountered an unexpected error\nGood luck !")
