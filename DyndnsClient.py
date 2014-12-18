#!/usr/bin/env python3
import requests, configparser, argparse, sys, os.path
from datetime import datetime
from subprocess import check_output



Username = 'your Username'
Password = 'Your secure password'
Host = 'www.ovh.com' # replace this with your dyndns' domain provider
Hostname = 'subdomain.domain.net' # or 'domain.net'
User_Agent = "icefo's dyndns updater -- https://github.com/icefo/DyndnsClient" # or "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
Use_Https = True
Path_To_IpFile = "{}/".format(os.path.expanduser("~")) + '.DyndnsClientIpHistory'

if Use_Https:
    http_mode = 'https://'
else:
    http_mode = 'http://'



# Get the arguments, if any
parser = argparse.ArgumentParser(description="A simple dyndns update client in python 3\nhttps://github.com/icefo/DyndnsClient for more infos")
parser.add_argument("-ptc", "--Path_To_ConfigFile", help="You can call this script with a config file so specify the path here")
parser.add_argument("-ip", "--Force_Ip", help="You can override the detected ip by giving one here")
parser.add_argument("-HN", "--Force_Hostname", help="Use this if you want to update a specific hostname")
parser.add_argument("-F", "--Force_Ip_Update", help="Force ip update", action="store_true")
args = parser.parse_args()



# This parse an eventual config file
if args.Path_To_ConfigFile:
    config = configparser.RawConfigParser()
    config.optionxform = lambda option: option # option for case sensitive variable
    config.read(args.Path_To_ConfigFile)
    for key in config['Main']:
        globals()[key]  = config['Main'][key]

if args.Force_Hostname:
    Hostname = args.Force_Hostname



if args.Force_Ip:
    myip = args.Force_Ip
else:
    # find the ip with a dns query and raise an error if something goes wrong
    try:
        myip = check_output(["dig +short myip.opendns.com @resolver1.opendns.com"], shell=True, universal_newlines=True)
        myip = str(myip)[:-1]
    except Exception as e:
        print("Impossible to find the ip, the script will exit with the 1 error code -- ",str(datetime.now()), file=sys.stderr)
        print(e, file=sys.stderr)
        print("", file=sys.stderr) # make a newline between log entries
        sys.exit(1)



if not args.Force_Ip_Update:
    #check if the ip is still the same
    if not os.path.isfile(Path_To_IpFile):
        with open(Path_To_IpFile, 'w') as f:
            f.write('0.0.0.0\n0.0.0.0\n0.0.0.0\n0.0.0.0\n0.0.0.0')
    
    with open(Path_To_IpFile, 'r') as f:
        IpFile = f.read().split('\n')[-4:]
    
    if (myip == IpFile[-1]):
        print('The ip', myip, 'hasn\'t changed since last check' + ' -- ' + str(datetime.now()))
        sys.exit(0)
    else:
        IpFile.extend([myip])
        with open(Path_To_IpFile, 'w') as f:
            f.write('\n'.join(IpFile))



# Ip update happend below
payload = {'hostname': Hostname, 'myip': myip, 'system': "dyndns"}
url = http_mode + Host + '/nic/update'
headers = {'User-Agent': User_Agent}
auth = requests.auth.HTTPBasicAuth(Username,Password)
try:
    r = requests.get(url, params=payload, auth=auth, headers=headers)
except Exception as e:
    # Close the script if something unexpected happen
    # Can be connection timeout, connection reset by peer, no dns...
    print("Something bad happened -- "+ str(datetime.now()), file=sys.stderr)
    print(e, file=sys.stderr)
    print("", file=sys.stderr) # make a newline between log entries
    sys.exit(2)

# raise an exception if the server answered with and 4XX or 5XX code
try:
    r.raise_for_status()
except Exception as e:
    print("Http server answered to the update query with an 4xx or 5xx code, that's bad", file=sys.stderr)
    print(e, " -- ", str(datetime.now()), file=sys.stderr)
    print("", file=sys.stderr) # make a newline between log entries
    sys.exit(3)

if r.text.startswith('good'):
    print("Ip correctly updated the new ip is", myip," -- ", str(datetime.now()))
elif r.text.startswith('nochg'):
    print("The server answered to the request with no_change.")
    print("Except if you forced the ip update, this shouldn't happen. Updated ip : ", myip," -- ", str(datetime.now()))
