Welcome to the README file for my GitHub repository! This repository contains several Python scripts that enable scanning of either a URL or an IP address and store the open ports found during the scan in Redis, MongoDB, Oracle, and MySQL databases. These scripts can be run either locally or through a Docker container.

The scripts are designed to prompt the user for action if they try to scan an IP address that is already stored in any of the databases. The user can choose to overwrite the existing data or use it. If they choose not to take any action, they can exit the application by typing "No." If there is no stored data, the script will initiate a new scan and store the information in all the databases using the IP address as the identifier.

It is important to note that the scripts require configuration files to connect to the different databases. Before running the scripts, the user should update the configuration files with the relevant database connection details.

Here is a brief overview of each script in this repository:

Scan: This script scans a host and stores information about the open ports found in the Redis database as an IP address. If the host has been scanned before, the script will prompt the user to either use the stored data or overwrite it. If the user chooses not to take any action, the script will exit. If there is no stored data, the script will initiate a new scan and store the information in all the databases using the IP address as the identifier.

Profile: This script allows the user to scan the open ports of a specified IP address and store the information in a profile in the Redis database.

Export: The "export_rdis.py" script can export data that has been cached in Redis into CSV, XML, and JSON formats.

HTML: This script performs port scanning on one or more URLs provided by the user. It uses the Nmap library to scan for open ports on each URL and saves the results to the Redis, MongoDB, Oracle, and MySQL databases. The program also generates an HTML report for each scanned URL, which includes information on the open ports and services detected, as well as the date and time of the scan. The user is prompted to choose whether to use existing data from previous scans or overwrite it with new data. The program uses multithreading to speed up the port scanning process.

MySQL: This directory contains code for storing all the ports information in Redis and MySQL databases.

 database_connectivity: this folder ensures that the database connection code is organized and reusable across multiple scripts. It simplifies the process of connecting to the Oracle, MongoDB, Redis, and MySQL databases, allowing for efficient data storage and retrieval during the scanning process.