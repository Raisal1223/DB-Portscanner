# It is capable of storing the ports informaiton into Redis and MySQL DB.

# Beta Version : 0.05

# Modules used for this script
import mysql.connector
import redis
import socket
import threading
from queue import Queue
import uuid
import os

# Define the unique identifier for this scan
scan_id = str(uuid.uuid4())

# Function to establish a new MySQL connection
def connect_mysql():
    try:
        host = "localhost"
        port = 3306
        user = "root"
        # Establish a new MySQL connection
        mysql_db = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
        )
    
        return mysql_db
    except (ConnectionError, TimeoutError) as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    
# Function to establish a new Redis connection
def connect_redis(host="localhost", port=6379, db=2):
    try:
        redis_db = redis.Redis(host=host, port=port, db=db)
        return redis_db
    except (ConnectionError, TimeoutError) as e:
        print(f"Error connecting to Redis: {e}")
        return None

# Function to read the previous database choice from a file
def read_db_choice():
    try:
        with open('db_choice.yaml', 'r') as f:
            db_choice = f.readline().strip()
            if db_choice:
                print(f"Currently connected to '{db_choice}' database.")
                choice = input("Do you want to switch the database? (y/n) ")
                if choice.lower() == "y":
                    os.remove('db_choice.yaml')
                    return None
                else:
                    return db_choice
            else:
                return None
    except FileNotFoundError:
        # Create db_choice.yaml if it doesn't exist
        open('db_choice.yaml', 'w').close()
        return None
    except:
        return None


# Function to write the current database choice to a file
def write_db_choice(db_choice):
    try:
        with open('db_choice.yaml', 'w') as f:
            f.write(db_choice)
    except:
        pass


# Read the previous database choice
db_choice = read_db_choice()

# Connect to MySQL and Redis
mysql_db = None
redis_db = None

if db_choice:
    # Attempt to connect to the database choice stored in the file
    if db_choice == "mysql":
        mysql_db = connect_mysql()
    elif db_choice == "redis":
        redis_db = connect_redis()
else:
    # Prompt user for database choice if not stored in file
    while not db_choice:
        db_choice = input("Enter the database to write to (1 for MySQL, 2 for Redis): ").strip().lower()
        if db_choice == "1":
            db_choice = "mysql"
            mysql_db = connect_mysql()
            if mysql_db is None:
                db_choice = None
        elif db_choice == "2":
            db_choice = "redis"
            redis_db = connect_redis()
            if redis_db is None:
                db_choice = None
        else:
            db_choice = None
        if not db_choice:
            print("Invalid database choice. Please try again.")

# Store the current database choice
write_db_choice(db_choice)

# Create a cursor object to interact with the MySQL database
mycursor = None

# Create a new database in MySQL
if db_choice == "mysql":
    mycursor = mysql_db.cursor()
    mycursor.execute("CREATE DATABASE IF NOT EXISTS PortScanner")
    mycursor.execute("USE PortScanner")

    # Create table to store scan results in MySQL
    mycursor.execute("CREATE TABLE IF NOT EXISTS ScanResults (id INT AUTO_INCREMENT PRIMARY KEY, destination VARCHAR(255), port_number INT, status VARCHAR(255)) ENGINE=InnoDB;") 

# Define lock for thread synchronization
object_lock = threading.Lock()

# Set default timeout for socket connections
socket.setdefaulttimeout(2)

# Prompt user for destination and resolve IP addresses
destinations = input("Enter the destinations: ").split(",")
hostIPs = []
for destination in destinations:
    hostIP = socket.gethostbyname(destination.strip()) 
    hostIPs.append(hostIP)
print("Scanning the host IP:", hostIPs)

# Define port scanning function
def portscanner(destination, hostIP, ports):
    soxx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        connection = soxx.connect((hostIP, ports))
        with object_lock:
            print("The port", ports, "is currently open.")
        # Save scan result to the selected database
            if db_choice == "mysql":
                sql = "INSERT INTO ScanResults (destination, port_number, status) VALUES (%s, %s, %s)"
                val = (destination, ports, "open")
                mycursor.execute(sql, val)
                mysql_db.commit()
            elif db_choice == "redis":
                profile = f"{scan_id}_{'_'.join(destinations)}"
                redis_db.hset(profile, ports, "open")
        connection.close()
    except:
        pass

# Set up queue and worker threads
que = Queue()
threads = []
for hostIP, destination in zip(hostIPs, destinations):
    for i in range(500):
        t = threading.Thread(target=portscanner, args=(destination, hostIP, i,))
        threads.append(t)
        t.start()

# Populate queue with port numbers
for ports in range(1, 1000):
    que.put(ports)

# Wait for all worker threads to finish
for t in threads:
    t.join()

# Close database connections
if mysql_db is not None:
    mysql_db.close()

if redis_db is not None:
    redis_db.close()