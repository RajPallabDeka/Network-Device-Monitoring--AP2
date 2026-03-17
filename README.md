# Network Device Monitoring Automation (AP2)

## Project Overview

This project is a **Python-based network automation tool** designed to **monitor the reachability of network devices** using the **Netmiko** library.
Netmiko is a Python library that automates network devices over **SSH and Telnet**. It is built on top of **Paramiko**, providing device-specific features and greater control for network automation tasks.
The script compares the **previously stored device status** with the **current status** obtained during execution. After comparison, the previous status is overwritten with the current status. An email alert is triggered **only when a status change is detected** (UP ↔ DOWN ↔ PACKET DROP).
The script is automated using **cron**, scheduled to run **every 5 minutes, 24×7**, making it suitable for **real-world NOC-style monitoring scenarios**.
The script also includes exception handling for SSH timeouts,Authentication failures,Unreachable devices,SMTP connection issues.

---

## Objectives

- Automate ICMP reachability (ping) checks for network devices  
- Persistently store device status for comparison  
- Automate logging link's status history along with timestamps  
- Send email notifications (with timestamps) when a link status changes  
- Gracefully handle SSH, timeout, and authentication failures  
- Run fully unattended using **cron jobs**

---

## Technologies Used

- **Python 3**
- **Netmiko** – SSH connection , Sending commands , receiving output 
- **smtplib** – Connecting to smtp server and sending email  
- **email.message** - Email formatting 
- **concurrent.futures(ThreadPoolExecutor)** – Parallel execution of code
- **time** - for timestamps 
- **os** - specify file locations 
- **Linux Cron** – Task scheduling
- **Linux OpenConnect** - for VPN connection
- **Cisco IOS / IOS-XR / NX-OS devices**

---

## How the Script Works

### Script 1 

1. The script connects to network devices using **Netmiko**
2. Sends ICMP ping commands from the device CLI
3. Parses ping output to determine link status:
   - `UP` → 100% success rate  
   - `DOWN` → 0% success rate  
   - `DROP` → Packet loss detected
4. Writes the result to a **device-specific text file**

### Script 2

1. The script connects to network devices using **Netmiko**
2. Sends ICMP ping commands from the device CLI
3. Parses ping output to determine link status:
   - `UP` → 100% success rate  
   - `DOWN` → 0% success rate  
   - `DROP` → Packet loss detected
5. Reads the **previous status** from the same file
6. Compares previous and current status:
   - If unchanged → **No action**
   - If changed → **Email alert sent**
7. Updates the device specific text file with the current status
8. Script exits cleanly and waits for the next cron execution

---

## Project Structure
```
Network-Device-Monitoring--AP2/
                              ├── Photos/
                              │   ├── Device_Status_history.png
                              │   ├── Device_Status_history_1.png
                              │   ├── Email_alerts.png
                              │   └── contab.png
                              │
                              ├── Scripts /
                              │   ├── Current_Status.py
                              │   └── InitialStatus.py
                              │
                              ├── .gitignore
                              ├── LICENSE
                              └── README.md
```
---

## Challenges Faced and the solutions 

### 1.Unpredictable script and email outcome .
(Threading with global variable is dangerous for automation : )
Threads run at the same time simultaneously , they share memory . Global variables live in shared memory . That is all the threads running read and writes the same variable simultaneously . Order of execution becomes unpredictable and data gets overwritten , corrupted and inconsistent .
To overcome this challenge all the global scope variables were made local scope.

### 2.Corrupt output  
(Running multiple threads inside one Netmiko SSH session , Netmiko is not threading safe ) 
Netmiko maintains a internal state per SSH session like prompt , channel timing , input buffer , output buffer  . When multiple threads share one Netmiko connection commands get overlap , output gets mix , session hangs .
To overcome this challenge I created separate individual Netmiko connections for each thread.

### 3.Connection failure due to timeouts
(Netmiko send_command method’s read_timeout )
Since Netmiko’s send_command method’s read_timeout parameter’s default value is 10 sec , it was causing connection failure for which whole script was failing .
To overcome this challenge I increased the read_timeout value to 30 seconds.

### 4. Email delivery failure caused by not explicitly specifying the SMTP port in the smtplib.SMTP() object, which defaulted to port 25 and resulted in blocked or unsupported connections.
Since the original 25 is for server-to-server relay but often blocked for spam . And recommended default for secure email submission (STARTTLS) is 587.
To overcome this challenge I specifically pass the port number as 587 inside the smtplib.SMTP() object.

### 5. Cron unable to execute the script
To execute a Python script using cron, the absolute path to both the Python interpreter and the script must be specified. Cron does not load the user’s shell environment, so relative paths may fail.
If the script path contains spaces, it must be enclosed in double quotes (" ") to ensure correct execution.


---

## Future Enhancements 

- Packet capture and traffic analyzing (Integrating Wireshark )
- Integration of API to retrieve interface and routing data (Restconf/Netconf)
- Interface State change detection and Cause suggestion . 
- Integrating Grafana 
- Integration with GNS3 lab  

---

## Author : 

Raj Pallab Deka
💼 Current Role: [Network Field Engineer], [Coforge] , [Under Government NIC-NKN Project]
🌐 Network Automation & Cybersecurity Enthusiast
🔗 GitHub: https://github.com/RajPallabDeka 🔗 LinkedIn: https://www.linkedin.com/in/your-profile

---

⭐ If you like this project, consider giving the repository a star — it helps the profile stand out!
