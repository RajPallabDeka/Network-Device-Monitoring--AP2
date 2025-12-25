from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
import os
os.chdir("/home/dekaraj22/Desktop/Projects /Automation Projects/Automation Project 2")

"""
Network Initial Status Capturing Script

The script establishes an SSH connection to a Cisco IOS-XE device using
Netmiko and performs ICMP reachability tests to multiple network
endpoints representing different network segments.

This script is designed to capture the initial status of the network
links connected to the assumed core router (Cat8kv). Each targeted
device is pinged from the Cat8kv router, and the resulting status
(UP, DOWN, PACKET DROP) is written to a text file named after the
specific device.

The initial status of the links (text files) can be further used for
status tracking and automation purposes.

Raises:
    NetmikoTimeoutException: If the SSH connection times out.
    NetmikoAuthenticationException: If authentication fails.

Modules and Technologies Used:
- Python
- Netmiko (SSH-based network automation)
- Cisco IOS-XE devices
- os

Environment: Linux

Author: Raj Deka

"""

def Initial_status(ip_addr , dev_name):
    """
    Checks the reachability of a network device and writes the result
    to a text file named after the specific device.

    Arguments:
        ip_addr (str): 
            -IP address of the targeted device.
        dev_name (str): 
            -Name of the device, used to create
             the output status file (<device_name>.txt).

    Side Effects:
        Creates a text file containing the link status.

    Returns :
        None

    The function sends ICMP echo requests to the target device using
    Netmiko and determines whether the link is UP, DOWN, or experiencing
    packet drops based on the ping success rate.
    """
    cat8kv.enable()
    ping = cat8kv.send_command(f"ping {ip_addr} repeat 10" , read_timeout=30) # A variable ping is created that store the output of the ping command that sends ICMP echo requests to the specified argument of the ip_addr parameter with a repeat count of 10 and Netmiko send_command method's read_timeout 30 sec
    file = open(f"{dev_name}.txt" , "w") #The open() function is invoked to create a text file whose name is derived from the dev_name parameter, open it in write mode,and store the returned file object in the variable "file"
    
    if "Success rate is 100" in ping : #if "Success rate is 100" detected in ping variable , write "Link is up" in the text file 
        file.write("The Link is up")
    elif "Success rate is 0" in ping : #if "Success rate is 0" detected in ping variable , write "Link is down" in the text file
        file.write("The Link is down")
    else : #if "Success rate is rather than 0 and 100" detected in ping variable , write "Drop Detected" along with the ping output in the text file
        file.write(f"Drop detected \n {ping}")
    file.close()

if __name__=="__main__" :
    try :

        cat8kv =  ConnectHandler(
            device_type="cisco_xe",
            host=" ",
            username=" ",
            password=" ",)#This method creates a Netmiko Connection object by establishing an SSH connection to a network device and store the returned object in the variable and is later used to send command and recieve outputs



        Initial_status("10.10.20.35", "IOS_XRv")
        Initial_status("10.10.20.40", "N9k")
        Initial_status("10.10.20.50", "DeveloperSegment")
        Initial_status("10.10.10.254", "test_segment")
        cat8kv.disconnect()

    except NetmikoTimeoutException : 
        print("Connection cannot be establish at the moment , please try again later")
    except NetmikoAuthenticationException : 
        print("Connection failed due to authentication issue . ")



