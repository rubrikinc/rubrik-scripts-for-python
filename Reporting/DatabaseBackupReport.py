#!/usr/bin/env python
# This script comes with no warranty use at your own risk
#
# Title: Database Backup Report
# Author: Maka Heng - Rubrik Professions Services
# Date: 10/16/2019
# Python ver: 3.7.4
#
# Description:
#
# Report on SQL databases protected by Rubrik

######################################## User Provided Variables #################################
# Cluster IP Address and Credentials
NODE_IP_LIST = [] # Ex. ['10.255.2.198', '10.255.2.199']
USERNAME = ""
PASSWORD = ""
NUMBER_OF_NODES = (len(NODE_IP_LIST) - 1)

######################################## End User Provided Variables ##############################
import os
import time, datetime
import base64
import asyncio
from aiohttp import ClientSession, TCPConnector
import requests
import json
from random import randint
import sys
import argparse
import urllib3
import csv
import datetime
import pprint

# ignore certificate verification messages
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# instaniate prettyprinter
pp = pprint.PrettyPrinter(indent=4)

# datetime stamps
timestamp = time.strftime('%m-%d-%y_%H%M')

######################################## Custom Functions ##############################
def get_all_dbs(limit):
    offset = 0
    db_data = []
    hasMore = True
    while(hasMore):
        response_data = rubrik_get("v1", "/mssql/db?limit={}&offset={}".format(limit, offset))
        db_data += response_data["data"]
        hasMore = response_data["hasMore"]
        if hasMore == True:
            offset += limit
    return db_data

def merge_lists(l1, l2, key):
  merged = {}
  for item in l1+l2:
    if item[key] in merged:
      merged[item[key]].update(item)
    else:
      merged[item[key]] = item
  return [val for (_, val) in merged.items()]

def checkFilePath(directory_path):
    if not os.path.exists(os.path.dirname(directory_path)):
        try:
            os.makedirs(os.path.dirname(directory_path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def save_dict_to_csv(csv_columns, dict_data, csv_file):
    try:
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")

def db_sort(databases):
   for database in databases:
        if database['isInAvailabilityGroup'] == True:
            database['recoveryModel'] = 'FULL'
        row = {'DatabaseName'               : database['name'],
               'DatabaseId'                 : database['id'],
               'RootType'                   : database['rootProperties']['rootType'],
               'Location'                   : database['rootProperties']['rootName'],
               'LiveMount'                  : database['isLiveMount'],
               'Relic'                      : database['isRelic'],
               'slaAssignment'              : database['slaAssignment'],
               'configuredSlaDomainName'    : database['configuredSlaDomainName'],
               'copyOnly'                   : database['copyOnly'],
               'recoveryModel'              : database['recoveryModel'],
               'effectiveSlaDomainName'     : database['effectiveSlaDomainName'],
               'isLogShippingSecondary'     : database['isLogShippingSecondary']}
        SORTED_DATABASE_LIST.append(row)

######################################## Generic Rubrik API Functions ##############################

def basic_auth_header():
    """Takes a username and password and returns a value suitable for
    using as value of an Authorization header to do basic auth.
    """

    credentials = '{}:{}'.format(USERNAME, PASSWORD)

    # Encode the Username:Password as base64
    authorization = base64.b64encode(credentials.encode())
    # Convert to String for API Call
    authorization = authorization.decode()

    return authorization


def rubrik_get(api_version, api_endpoint):
    """ Connect to a Rubrik Cluster and perform a GET operation """

    AUTHORIZATION_HEADER = {'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'Authorization': 'Basic ' + basic_auth_header()
                            }

    request_url = "https://{}/api/{}{}".format(NODE_IP_LIST[0], api_version, api_endpoint)

    try:
        api_request = requests.get(request_url, verify=False, headers=AUTHORIZATION_HEADER)
        # Raise an error if they request was not successful
        api_request.raise_for_status()
    except requests.exceptions.RequestException as error_message:
        print(error_message)
        sys.exit(1)

    response_body = api_request.json()

    return response_body

######################################## Async Functions ##############################
async def get(url, session):
    db_id = url.split('/mssql/db/', 1)[1].split('/snapshot',1)[0]

    AUTHORIZATION_HEADER = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Basic ' + basic_auth_header()
    }

    async with session.get(url, headers=AUTHORIZATION_HEADER, verify_ssl=False) as response:
        rpoInHours = 24
        now = datetime.datetime.utcnow()

        response_body = await response.read()

        try:
            snapshots = response_body.decode('utf8').replace("'", '"')
            snapshots = json.loads(snapshots)
            complianceStatus = 'Out Of Compliance'
            if len(snapshots['data']) > 0:
                latestSnapshot = datetime.datetime.strptime(snapshots['data'][00]['date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                diff = latestSnapshot - now 
                if (diff.seconds /3600) < rpoInHours:
                    complianceStatus = 'Compliant'
            else:
                latestSnapshot = 'No Snapshot Taken'
            DATABASE_SNAP_LIST.append({'DatabaseId' : db_id, 'BackupDate' : latestSnapshot, 'OutOfCompliance' : complianceStatus})
            print('Success: {}'.format(url))
        except:
            ERROR_LIST.append('Error: {}'.format(url))

async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    try:
        async with sem:
            await get(url, session)
    except Exception as error:
        ERROR_LIST.append(str(error) + ' {}'.format(url))
 
async def run():
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(500)

    # Create client session that will ensure we dont open new connection
    # per each request.
    try:
        async with ClientSession() as session:
            for url in REQUEST_URL:
                # pass Semaphore and session to every GET request

                task = asyncio.ensure_future(bound_fetch(sem, url, session))

                tasks.append(task)

            responses = asyncio.gather(*tasks)
            await responses
    except Exception as error:
        ERROR_LIST.append(error)


######################################## Main ##############################
DATABASE_LIST = []
SORTED_DATABASE_LIST = []
DATABASE_SNAP_LIST = []
REQUEST_URL = []
ERROR_LIST = []


# Start time
start_time = time.time()

print("Getting SQL DBs...\n")
DATABASE_LIST = get_all_dbs(1000)

print("Building the API calls...\n")
for db in DATABASE_LIST:
    api_endpoint = "/mssql/db/{}/snapshot".format(db["id"])
    random_list_index = randint(0, NUMBER_OF_NODES)
    node_ip = NODE_IP_LIST[random_list_index]
    REQUEST_URL.append("https://{}/api/{}{}".format(node_ip, 'v1', api_endpoint))

print("Executing the API calls.\n")
loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run())
loop.run_until_complete(future)

print("Sorting database list...\n")
db_sort(DATABASE_LIST)
MERGED_DATABASE_LIST = merge_lists(SORTED_DATABASE_LIST, DATABASE_SNAP_LIST , 'DatabaseId')

print("Writing to CSV file...\n")
fieldnames = ['DatabaseName', 'RootType', 'Location', 'LiveMount', 'Relic', 'BackupDate', 'OutOfCompliance', 'slaAssignment', 
              'configuredSlaDomainName', 'copyOnly', 'recoveryModel', 'effectiveSlaDomainName', 'isLogShippingSecondary', 'DatabaseId']
directory_path = 'rubrik_output/sql_report/'
checkFilePath(directory_path)
csv_file1 = directory_path + "{}_sql_report.csv".format(timestamp)
save_dict_to_csv(fieldnames, MERGED_DATABASE_LIST, csv_file1)

# Display errors
if ERROR_LIST:
    print("********* Errors *********\n")
    for error in ERROR_LIST:
        print(error)

# End time
elapsed_time = time.time() - start_time
elapsed_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
print("Elapsed time: {}\n".format(elapsed_time))