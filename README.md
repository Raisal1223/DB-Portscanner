The purpose of this script is to scan an URL or an IP address and have it cache it's open port to the Redis database. 
This script can be executed from the local machine and through the Docker container. Once an URL or an IP address is stored the data will be stored in the Redis database.
If the user decided to scan the same IP address the script will prompt the user if it want to overwrite the existing data or use the existing stored information. 
If the user does not want to take any action, typing "No" will exit out of the application.
Lastly if there are no data stored in the Redis database, the script will start a brand new scanning and store into the database with an IP address.