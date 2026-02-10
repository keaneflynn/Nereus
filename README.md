# Nereus
**Author**: Keane Flynn\
**Date**: 05/07/2025\
**Contact**: keaneflynn1@gmail.com

## Prerequisites
In your PostgreSQL database, the superuser will need to add the uuid-ossp extension. 
This can be done with the following command: `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`. 
Additionally, when you create the table for this in postgres, you will need to register  
the date, time, reader_id, and tag_id fields as 'unique()' fields so the upsert SQL 
command can function properly.

## Overview
Program to download Biomark IS1001 passive integrated transponder (PIT) antennas 
and append to a postgres database. This program functions by creating a socket 
connection to a specified IP addres and port and sending a Biomark-specified 
three-letter command to invoke a serial dump of PIT tag. The socket connection
will then grab and parse this serial data into a database-appendable format.
This data is then passed into a PIT tag database.

## Hardware & Configuration
The Nereus program is capable of runnning on any basic computer/server node. To allow for this program 
to grab data from a PIT antenna reader, the reader in question must be a Biomark 
model IS1001 reader with the Remote Communication Board equipped (I have personally
only made this work on the 24v variant of the IS1001, but the user manual doesn't
say that it will not work on a 12v variant). The IS1001 board actually has zero 
network capabilites, so you can think of this Remote Comms Board as its own 
computer that is just gathering serial data through the GPIO pins from the IS1001.
Given this, we need to set some parameters on the Remote Comms Board to allow for
proper network communication. They are as follows:
* Check the 'Use the following IP configuration' button
	* This allows for a static IP address allocation
* IP Address: Set specified address
* Subnet Mask: Set specified subnet mask
* Default Gateway: Set specified default gateway
* MTU Size: 1400
	* This is the default as it is shipped from Biomark. If the connection
	  is slower it might need to be lowered to 1250 per Biomark's guidance
* TCP Re-Transmission Timeout (ms): 500

## Input & Output
All input parameters can be found using the `python nereus.py -h` flag
### Input
*Client File*: File path to `.clients` file in the following json format:
```
{
	"ip_address_1": 
	{
		"latitude": "99.9999",
		"longitude": "-99.9999"
	},
	"ip_address_2":
	{
		"latitude": "99.9998",
		"longitude": "-99.9998"
	}
}
```

### Output
*UUID*: Unique identifier character appended by the PostgreSQL client\
*date*: YYYY-MM-DD date format\
*time*: HH:MM:SS.SSS timezoneless format\
*reader_id*: Reader ID value set within the IS1001 menu\
*tag_id*: PIT tag recorded by IS1001\
*latitude*: WGS84 latitude of PIT antenna\
*longitude*: WGS84 longitude of PIT antenna\
*ip_address*: IP address setup in IS1001 Remote Communication Board 

## How To Use
Issue the following command in your terminal block to clone the repository:
```
git clone https://github.com/keaneflynn/Nereus.git
```
You will then need to change directory into the newly downloaded repo `cd Nereus/`

Create a python virtual environment to install the correct dependencies
```
python -m venv ./
```
Then activate the virtual environment:
```
source bin/activate
```
Install the necessary dependencies for this repository:
```
pip install -r requirements.txt
```
Lastly exit the virtual environment with `deactivate`

This program is made to run as a cronjob, but can be run from the terminal
manually in the following way: `python nereus.py src/.clients`

## Running From Crontab
This program is primarily designed to be run on a server as a cronjob. 
To make this work, you will need to modify the crontab file using the following 
command:
```
crontab -e
```
You will then need to insert a new line at the end of this file with the info
from the cron/sampleCron.txt file:
```
0 */1 * * * /path/to/venv/bin/python3 /path/to/venv/nereus.py /path/to/venv/src/.clients 
> /path/to/venv/errorLogs/ouput.log 2>&1
```
And just like that, the program will be set to run at the top of every hour.

## Troubleshooting
Please see error logs as referenced above to troubleshoot data transmission issues. 
Most of the issues likely to arise with this software will derive from hardware issues
from the PIT antenna systems (i.e., disconnected solar, rodents messed with wires, etc.).
Please refer to the network connections database to troubleshoot connectivity issues 
prior to making software adjustments.
