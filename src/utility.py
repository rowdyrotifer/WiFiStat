import socket
import subprocess
import sys
from sys import platform

def platform_is(test):
    return platform == test if platform != "darwin" else test == "osx";

#Simple wrapper around subprocess to run commands...
def cmd(subprocess_args, short=True, use_shell=False):
    if short:
        return subprocess.Popen(subprocess_args, stdout=subprocess.PIPE, shell=use_shell).communicate()[0].rstrip()
    else:
        return subprocess.Popen(subprocess_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=use_shell).communicate()
    
#Python 2 & 3 compatible "press enter to continue" 
def wait(prefix):
    if sys.version_info[0] == 2:
        raw_input(prefix + "Press enter to continue...")
    else:
        input(prefix + "Press enter to continue...")

#Automatically determine the WiFi network name.
def get_best_network_name():
    if platform_is("osx"):
        return cmd(["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | awk '/ SSID/ {print substr($0, index($0, $2))}'"], use_shell=True)
    else:
        return "network"

#IP validator
def is_valid_ip(ip):
    try: socket.inet_aton(ip); return True
    except socket.error: return False

#Attempts to get LAN router IP to ping, returns Google's DNS server (8.8.8.8) otherwise.
def get_best_ping_ip():
    if platform_is("osx"):
        return cmd(["netstat -rn | grep default | awk '{print $2}'"], use_shell=True)
    else:
        return "8.8.8.8"

#Determines the best speedtest server from the "speedtest-cli --list" command.
def getspeedtest_server():
    return cmd(["speedtest-cli --list | sed -n 3p | awk 'BEGIN { OFS = \")\"} {print $1}' | sed s'/)//g'"], use_shell=True)
