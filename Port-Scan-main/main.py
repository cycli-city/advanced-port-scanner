from queue import Queue
import socket
import threading
from IPy import IP
from datetime import datetime

target = input("Enter Target: ")
proxy_ip = input("Enter a Proxy IP (optional): ")

print("""
  _____           _          _____                 
 |  __ \         | |        / ____|                
 | |__) |__  _ __| |_ _____| (___   ___ __ _ _ __  
 |  ___/ _ \| '__| __|______\___ \ / __/ _` | '_ \ 
 | |  | (_) | |  | |_       ____) | (_| (_| | | | |
 |_|   \___/|_|   \__|     |_____/ \___\__,_|_| |_|
""")

queue = Queue()
open_ports = []

services = {
21:"FTP",
22:"SSH",
23:"Telnet",
25:"SMTP",
53:"DNS",
80:"HTTP",
110:"POP3",
143:"IMAP",
443:"HTTPS",
3306:"MySQL",
3389:"RDP",
8080:"HTTP-Proxy"
}

def get_banner(sock):
    try:
        sock.settimeout(2)
        banner = sock.recv(1024)
        return banner.decode().strip()
    except:
        return ""

def check_ip(ip):
    try:
        IP(ip)
        return ip
    except ValueError:
        return socket.gethostbyname(ip)

def portscan(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        result = sock.connect_ex((check_ip(target), port))

        if result == 0:
            return sock
        else:
            return False

    except:
        return False

def get_ports(mode):

    if mode == 1:
        ports = [20,21,22,23,25,53,80,110,143,443]
        for port in ports:
            queue.put(port)

    elif mode == 2:
        for port in range(1,1025):
            queue.put(port)

    elif mode == 3:
        for port in range(1,65536):
            queue.put(port)

    elif mode == 4:
        start = int(input("Enter starting port: "))
        end = int(input("Enter ending port: "))

        for port in range(start,end+1):
            queue.put(port)

def worker():

    while not queue.empty():

        port = queue.get()
        config = portscan(port)

        if config:

            service = services.get(port,"Unknown")

            try:
                banner = get_banner(config)

                print(f"[OPEN] Port {port} | {service}")

                if banner:
                    print(f"       Banner: {banner}")

            except:
                print(f"[OPEN] Port {port} | {service}")

            open_ports.append(port)

        queue.task_done()

def run_scanner(threads,mode):

    get_ports(mode)

    thread_list = []

    for t in range(threads):

        thread = threading.Thread(target=worker)
        thread_list.append(thread)

    start_time = datetime.now()

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

    end_time = datetime.now()

    print("\nScan Completed")
    print("Open Ports:",open_ports)
    print("Time taken:",end_time-start_time)

mode = int(input("""
Enter Mode
1 - Common Ports
2 - 1-1024
3 - Full Scan
4 - Custom Range

Choice: """))

threads = int(input("Enter number of threads: "))

run_scanner(threads,mode)