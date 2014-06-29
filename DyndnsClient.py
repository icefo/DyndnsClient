#!/bin/env python3
from urllib.request import Request, urlopen
from urllib.error import  URLError
import base64, re, configparser, argparse

Username = 'My Username'
Password = 'My Secure Password'
Host = 'www.ovh.com' # replace this with your dyndns' domain name 
Hostname = ['subdomain.domain.net']
Whatsmyip = 'http://checkip.dyndns.com/', 'http://wtfismyip.com/text'
User_Agent = "icefo's dyndns updater" # or "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
use_https = True

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
	Whatsmyip = Whatsmyip.split(' , ') # make list
	Hostname = Hostname.split(' , ')
	if (Use_Https.lower() == 'true'):
		Use_Https = True
	else:
		Use_Https = False


if use_https:
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



credentials = Username + ':' + Password
credentials = base64.standard_b64encode(bytes(credentials, "utf8"))
credentials = 'Basic ' + str(credentials)[2:-1]

url_1 = http_mode + Host + '/nic/update?system=dyndns' + '&hostname=' + ','.join(Hostname) + '&myip=' + myip
headers_2 = {'Host': Host, 'Authorization': credentials, 'User-Agent': User_Agent}


print(HTTP_Client(url_1, headers_2)[0]) # /!\ no error handling and no https cert check --> use requests.get for that ?

