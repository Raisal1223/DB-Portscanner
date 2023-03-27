# Creates HTML report for each url that is being scanned

# Import required modules
import socket
import threading
from queue import Queue
import redis
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import nmap
import os 

# Create a directory to store the reports
directory = "html_reports"
if not os.path.exists(directory):
    os.makedirs(directory)

# Set up Jinja2 template environment
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('report_template.html')

# Connect to Redis server from your local machine
r = redis.Redis(host='localhost', port=6379, db=1)

# Set the default timeout for the socket to 2 seconds
socket.setdefaulttimeout(2)

# Define the lock object for consistent data storing in Redis
object_lock = threading.Lock()

# Retrieve the URL that the user wants to scan
destinations = input("Enter the URLs you want to scan: ").split(",")

# Define the profile name
profile = input("Enter the profile name: ")

# Define the IP address from the provided URL
for destinations in destinations:
    hostIP = socket.gethostbyname(destinations.strip())
    ip_address = hostIP
    print("Scanning the host IP for", destinations, ":", hostIP)

# Showing the time of the scan
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d, %H:%M:%S")
    print("Time of the scan is: ", now_str)

# Define the portscanner function to show only the open ports
    open_ports = []

    def portscanner(ports):
        soxx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            connection = soxx.connect((hostIP, ports))
            network_mapper = nmap.PortScanner()
            service = network_mapper.scan(hosts=hostIP, arguments=f"-sV -p{ports}")['scan'][hostIP]['tcp'][ports]['name']
            status = "open"
            print(f"The port {ports}, and the service {service} is currently {status}.")
            with object_lock:
                open_ports.append(ports)
                r.hset(profile, str(ports), f"{service}, {status}")
            connection.close()      
        except:
            pass

# Queue class is defined
    que = Queue()

# Define the threading process to scan the ports
    def threader():
        while True:
            nodes = que.get()
            portscanner(nodes)
            que.task_done()

# Check if the profile exists in the database
    if r.exists(profile):
    # If the data exists prompt the user what action they want to perform
        user_choice = input(f"Data for {profile} already exists. Do you want to use the previous data (Y/N/O(verwrite))?: ")
        if user_choice in ('Y', 'y', 'yes', 'Yes'):
            existing_data = r.hgetall(profile)
        # Use the previous data
            print("Using the previous data...")
            for key, value in existing_data.items():
                print(f"Port: {key}, Status: {value}")
        elif user_choice in ('o', 'overwrite', 'O', 'Overwrite'):
        # Overwrite the previous data
            print("Overwriting the previous data...")
            for ports in range(10000):
                threads = threading.Thread(target=threader)
                threads.daemon = True
                threads.start()

            for nodes in range(1, 10000):
                que.put(nodes)

            que.join()
        elif user_choice in ('n', 'no', 'N', 'No'):
        # If the user does not want to take any action
            print("No action is needed.")   
        else:
        # Invalid option, exit the program
            print("Invalid option selected. Exiting the program...")
            exit()
    else:
    # No data for the current destination IP exists, start the scan
        for ports in range(10000):
            threads = threading.Thread(target=threader)
            threads.daemon = True
            threads.start()

        for nodes in range(1, 10000):
            que.put(nodes)

        que.join()

# Generate the report for each destination
    host_profile = profile
    data = {k.decode(): v.decode() for k, v in r.hgetall(host_profile).items()}
    now_str = now.strftime("%Y-%m-%d, %H:%M:%S")
    report = template.render(destination=destinations, data=data, now_str=now_str, ip_address=ip_address)


# Export the report to an HTML file
    scan_name = input(f"Enter the scan name for {destinations}: ")
    file_name = f"{scan_name}_{destinations}.html"
    with open(f"{directory}/{file_name}", 'w') as file:
        file.write(report)


# Start the port scanning process for each destination URL
    for destination in destinations:
        portscanner(destination)