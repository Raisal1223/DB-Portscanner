# Add the required module for this application
import socket
import threading
from queue import Queue
import redis

# Connect to Redis server from your local machine
r = redis.Redis(host='localhost', port=6379, db=1)

# Uncomment line 12 and 13 to have it communicate to the Docker container
# docker_container = "172.17.0.2"
# r = redis.Redis(host=docker_container, port=6379, db=2)

# Set the default timeout for the socket to 2 seconds
socket.setdefaulttimeout(2)

# adding lock object for consistent data storing in Redis
object_lock = threading.Lock()

# Enter an URL/IP you want to scan
destination = input ("Enter the destination: ")

# Retrieve the IP address from the URL
hostIP = socket.gethostbyname(destination)
print("Scanning the host IP: ", hostIP)

# portscanner function to discover "open" ports
def portscanner(ports):
    soxx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        connection = soxx.connect((hostIP, ports))
        with object_lock:
            print("The port", ports, "is currently open.")
            r.hset(hostIP, str(ports), 'open')
        connection.close()
    except:
        pass

# que object defined
que = Queue()

# Here is the function to start the threading process
def threader():
    while True:
        nodes = que.get()
        portscanner(nodes)
        que.task_done()

# Check if data for the current destination IP exists
if r.exists(hostIP, 'open'):
    # If the data exists prompt the user what action they want to perform
    user_choice = input(f"Data for {hostIP} already exists. Do you want to use the previous data (Y/N/O(verwrite))?: ")
    if user_choice in ('Y', 'y', 'yes', 'Yes'):
        existing_data = r.hgetall(hostIP)
        # Use the previous data
        print("Using the previous data...")
        for key, value in existing_data.items():
            print(f"Port: {key}, Status: {value}")
    elif user_choice in ('o', 'overwrite', 'O', 'Overwrite'):
        # Overwrite the previous data
        print("Overwriting the previous data...")
        for ports in range(150):
            threads = threading.Thread(target= threader)
            threads.daemon = True
            threads.start()

        for nodes in range (1, 1000):
            que.put(nodes)

        que.join()
    elif user_choice in ('n', 'no', 'N', 'No'):
        # If the user do not want to take any action
        print("No action is needed.")   
    else:
        # Invalid option, exit the program
        print("Invalid option selected. Exiting the program...")
        exit()
else:
    # No data for the current destination IP exists, start the scan
    for ports in range(150):
        threads = threading.Thread(target= threader)
        threads.daemon = True
        threads.start()

    for nodes in range (1, 1000):
        que.put(nodes)

    que.join()    