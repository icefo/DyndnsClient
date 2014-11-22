===============================================
DyndnsClient - Simply update your dyndns domain
===============================================

This script update your dyndns domain

Requirements
============
- ``python >= 3.1``
- ``requests``
- ``dig``

dig is a command line dns utility

To install requests and dig look for python3-requests and dig in your package manager

Tested on ovh servers but should work with every standard dyndns server

Installation:
=============

Edit and paste the DyndnsConfig file in the /root directory

Paste the DyndnsClient.py file in the /usr/bin directory

Paste this in the /etc/crontab file: (check the ip every 10 minutes)
``*/10 * * * * root DyndnsClient.py -ptc '/root/DyndnsConfig' >> "/var/log/DyndnsClient.log" 2>> "/var/log/DyndnsClient_error.log"``

Paste the DyndnsClient file in /etc/logrotate.d

You're done !

