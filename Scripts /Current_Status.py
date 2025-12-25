from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
import os
import smtplib
import time 
from email.message import EmailMessage
from concurrent.futures import ThreadPoolExecutor
os.chdir("/home/dekaraj22/Desktop/Projects /Automation Projects/Automation Project 2")

"""
Network Link Status Monitoring and Alert Automation Script

This script monitors the reachability status of multiple network devices by
performing periodic ICMP tests from a Cisco IOS-XE router using Netmiko.
It detects link state changes by comparing the current status with a
previously recorded status and sends email alerts when a change is detected.

Core functionality includes:
- Establishing SSH connections to a Cisco IOS-XE device
- Performing ICMP reachability tests to multiple network devices
- Overwriting current link status to device-specific text files
- Maintaining a timestamped history of link state changes
- Comparing previous and current link states
- Sending SMTP email alerts upon state transitions
- Executing checks concurrently using a thread pool

The script is designed to be executed periodically (via cron) and
supports concurrent monitoring of multiple devices using
ThreadPoolExecutor for improved efficiency.

Raises:
    NetmikoTimeoutException: If the SSH connection times out.
    NetmikoAuthenticationException: If authentication fails.

Modules and Technologies Used:
- Python
- Netmiko (SSH-based network automation)
- smtplib and email.message (SMTP email alerts)
- concurrent.futures.ThreadPoolExecutor (multithreading)
- Cisco IOS-XE devices
- time
- os

Execution Model:
- Each device is represented as an object of the Devices class
- Initial link state is read from disk
- Current link state is evaluated live
- State changes trigger automated email notifications
- Multiple devices are processed in parallel threads

Environment:
- Linux
- cron-based monitoring 

Author: Raj Deka

"""



def Init_status(dev_name):
    """
    Reads the text file named after specific devices and returns a value for further comparision .

    Arguments : 
        dev_name: Name of the device , used to read
                    the output status file (<device_name>.txt).

    Returns:
        str: 
            One of the following values based on the link status:
            - "up"   : 100% ICMP success rate
            - "down" : 0% ICMP success rate
            - "drop" : packet loss detected
                    
    The function uses membership operator (in) to fine specific keyword in the text file and returns
    a corresponding value"""
    counter_1 = None
    file = open(f"{dev_name}.txt","r")
    Content = file.read() # Content variable store the whole output of the text file 
    #using direct file.read() cause issue because file.read() reads full file , cursor move to EOF , second file.read() gets nothing to read as cursor at EOF , so we keep the output of file.read in a variable that will store the while as a constant 
    if "up" in Content:  # If "up" keyword is detected in the file , change counter_1 variable value to "up"
        counter_1 = "up"
    elif "down" in Content : # If "down" keyword is detected in the file , change counter_1 variable value to "down"
        counter_1 = "down"
    else : # If neither "up" or "down" keyword is detected in the file , change counter_1 variable value to "drop"
        counter_1 ="drop"
    file.close()
    return counter_1 

def Current_Status(ip_addr , dev_name ): 
    """
    The function establishes an SSH connection to a Cisco IOS-XE device using
    Netmiko and performs ICMP reachability tests to multiple network
    endpoints representing different network segments and overwrites the 
    result to a text file named after the specific device.

    Arguments : 
        ip_addr (str):
            IP address of the target device to be tested for reachability.
        dev_name (str):
            Device name used to generate output files:
            - <device_name>.txt
            - <device_name>_status_history.txt
   
    Side Effects:
        1. Overwrites an existing status text file (<device_name>.txt) with the
           current link state.
        2. Appends timestamped link status entries to
           <device_name>_status_history.txt.
        3. Establishes and terminates an SSH session with the network device.

    Returns:
        str: 
            One of the following values based on the link status:
            - "up"   : 100% ICMP success rate
            - "down" : 0% ICMP success rate
            - "drop" : packet loss detected
    """
    cat8kv =  ConnectHandler(
        device_type="",
        host=" ",
        username=" ",
        password=" ",
    )  

    counter_2 = None
    cat8kv.enable()
    ping = cat8kv.send_command(f"ping {ip_addr} repeat 10" , read_timeout=30)
    with open(f"{dev_name}_status_history.txt","a") as history : #This appends the link status with timestamp evrytime the script is executed , which is after every 5 minutes using cron 
        t1 = time.strftime("%d-%m-%Y") # Day / Month / Year
        t2 = time.strftime("%H:%M:%S") # Hour : Minute : Seconds
        if "Success rate is 100" in ping : # if Success rate is 100 detected in ping variable , write link is up with timestamp
            history.write(f"The Link is up ---{t2} {t1}\n")
        elif "Success rate is 0" in ping : # if Success rate is 0 detected in ping variable , write link is down with timestamp
            history.write(f"The Link is down---{t2} {t1}\n")
        else : # if Success rate is rather than 0 and 100 , detected in ping variable , write Drop detected with timestamp and the output in ping variable 
            history.write(f"Drop detected---{t2} {t1} \n {ping}\n")
    file = open(f"{dev_name}.txt" , "w")    
    if "Success rate is 100" in ping : # if Success rate is 100 detected in ping variable , overwrite link is up in the existing text file 
        file.write("The Link is up")
    elif "Success rate is 0" in ping : # if Success rate is 0 detected in ping variable , overwrite link is down in the existing text file 
        file.write("The Link is down")
    else :# if Success rate is 100 detected in ping variable , overwrite drop detected with the output in ping variable in the existing text file 
        file.write(f"Drop detected \n {ping}")
    file.close()
    file = open(f"{dev_name}.txt" , "r")
    Content = file.read()
    if "up" in Content :  # If "up" keyword is detected in the freshly overwritten text file , change counter_2 variable value to "up"
        counter_2 = "up"
    elif "down" in Content :  # If "down" keyword is detected in the freshly overwritten text file , change counter_2 variable value to "down"
        counter_2 = "down"
    else :  # If neither "down" or up" keyword is detected in the freshly overwritten text file, change counter_1 variable value to "drop"
        counter_2 =  "drop"
    file.close()
    cat8kv.disconnect()
    return counter_2

class Devices :
    """
    Represents a network device whose link status is monitored and automated
    for change detection and alerting.

    This class acts as an integration layer that:
    - Retrieves the previous link status from a stored status file
    - Determines the current link status via live ICMP testing
    - Compares both states to detect changes
    - Sends an email alert when a link state transition is detected

    Attributes:
        dev_name (str):
            Name of the network device used for file naming and alert messages.
        ip_addr (str):
            IP address of the device or endpoint used for ICMP reachability tests.
    """

    def __init__(self , dev_name , ip_addr):
        """
        Initializes a Devices Class object with device individual identity details.

        Arguments:
            dev_name (str):
                Name of the device.
            ip_addr (str):
                IP address used to test reachability.
        """
        self.dev_name = dev_name #instance attribute , every object created has its own dev_name 
        self.ip_addr = ip_addr #instance attribute , every object created has its own ip_addr
    def automation(self) :

        """
        Executes the link status monitoring and alert automation workflow.

        The method performs the following steps:
        1. Reads the previously recorded link status from disk.
        2. Determines the current link status using live ICMP tests.
        3. Compares previous and current states.
        4. Sends an email notification if a link state change is detected.

        Side Effects:
            - May send an email alert using SMTP if link status changes.
            - Relies on external files for status comparison.
            - Initiates outbound SMTP and SSH connections.

        Exceptions:
            Catches and prints any exception that occurs during
            email composition or transmission.

        Returns:
            None
            """

        Coun1 = Init_status(self.dev_name) # Coun1 stores the return value of Init_status() function , i.e. it stores the value of counter_1 (up,down,drop)
        Coun2= Current_Status(self.ip_addr,self.dev_name )# Coun1 stores the return value of Current_Status() function , i.e. it stores the value of counter_2(up,down,drop)
        time_date = time.strftime("%d-%m-%Y") # Day / Month / Year
        time_time = time.strftime("%H:%M:%S") # Hour : Minute : Seconds
        try:
            if Coun1 != Coun2 : #Here values of counter_1 and counter_2 are compared and if they dosent match an email is sent 
                mail = EmailMessage() #an EmailMessage object is created 
                mail["From"] = "labtest.raj@gmail.com" # Here ["From"] access the email header field 
                password = " " #EmailMessage has nothing to do with passwords or authentication , its just for the email format , we will simple pass mail["From"] and password to server.login(mail["From"],password), where passowrd is a variable where our password is sotred
                mail["To"] = "rajdeka.official@gmail.com" # Here ["To"] access the email header field 
                mail["Cc"] = "labtest.raj@gmail.com" # Here ["Cc"] access the email header field 
                to_list = ["rajdeka.official@gmail.com"] #List of To reciepents 
                cc_list = ["labtest.raj@gmail.com"] #List of CC reciepents
                all_receiver = to_list + cc_list #smtp ignores headers for delivery , we should pass it to smtp without headers 
                mail.set_content(f"Dear Team ,\n\nThe Catalyst-8kv to {self.dev_name} link state has changed since {time_time} on {time_date}.\nCurrent Link condition : {Coun2}\nKindly look into the matter and provide the RFO and ETR.\n\nRegards\nRaj Pallab Deka")
                server = smtplib.SMTP("smtp.gmail.com", 587 , timeout=30)#an smtplip.SMTP() object is created 
                server.starttls()
                server.login(mail["From"],password)
                server.sendmail(mail["From"],all_receiver,mail.as_string())
                server.close()
        except Exception as e:
            print(e)

if __name__=="__main__" :
    try : 
        
        IOS_XRv = Devices("IOS_XRv","10.10.20.35")
        N9k = Devices("N9k", "10.10.20.40")
        DeveloperSegment = Devices("DeveloperSegment","10.10.20.50")
        test_segment = Devices("test_segment","10.10.10.254")
        All_devices = [IOS_XRv,N9k,test_segment,DeveloperSegment] #List of all the Devices class objects 
    
        with ThreadPoolExecutor(max_workers=4) as THREADS: #A ThreadPoolExecutor object THREAD is created  
                result = THREADS.map(Devices.automation,All_devices)  #Here we are mapping all the Devices class object with the automation() method of Devices class                                  
        
    except NetmikoTimeoutException : 
        print("Connection cannot be establish at the moment , please try again later")
    except NetmikoAuthenticationException : 
        print("Connection failed due to authentication issue . ")
    except Exception as e :
        print(e)


        


    