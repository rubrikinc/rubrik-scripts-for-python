<<<<<<< HEAD
#!/usr/bin/env python
# This script comes with no warranty use at your own risk
#
# Title: pause_snapshot
# Author: Drew Russell - Rubrik Ranger Team
# Date: 03/29/2018
# Python ver: 3.6.4, 2.7.6
#
# Description:
#
# Pause and Resume a policy driven snapshot of a Virtual Machine

######################################## User Provided Variables #################################


# Cluster IP Address and Credentials
NODE_IP = ""
USERNAME = ""
PASSWORD = ""

# List of SLA Domains to Pause
SLA_DOMAIN_NAME_LIST = [] # Ex. ['Gold', 'Silver']


######################################## End User Provided Variables ##############################

import base64
import requests
import json
import sys
import time
from requests.auth import HTTPBasicAuth
import argparse


# ignore certificate verification messages
requests.packages.urllib3.disable_warnings()


# Generic Rubrik API Functions


def basic_auth_header(username, password):
    """Takes a username and password and returns a value suitable for
    using as value of an Authorization header to do basic auth.
    """
    return base64.b64encode(username + ':' + password)


def login_token(username, password):
    """ Generate a new API Token """

    api_version = "v1"
    api_endpoint = "/session"

    request_url = "https://{}/api/{}{}".format(NODE_IP, api_version, api_endpoint)

    data = {'username': username, 'password': password}

    authentication = HTTPBasicAuth(username, password)

    try:
        api_request = requests.post(request_url, data=json.dumps(data), verify=False, auth=authentication)
    except requests.exceptions.ConnectionError as connection_error:
        print(connection_error)
        sys.exit()
    except requests.exceptions.HTTPError as http_error:
        print(http_error)
        sys.exit()

    response_body = api_request.json()

    if 'token' in response_body:
        return response_body['token']
    else:
        print('The response body did not contain the expected token.\n')
        print(response_body)


def rubrik_get(api_version, api_endpoint, token):
    """ Connect to a Rubrik Cluster and perform a GET operation """

    AUTHORIZATION_HEADER = {'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'Authorization': 'Bearer ' + token
                            }

    request_url = "https://{}/api/{}{}".format(NODE_IP, api_version, api_endpoint)

    try:
        api_request = requests.get(request_url, verify=False, headers=AUTHORIZATION_HEADER)
        # Raise an error if they request was not successful
        api_request.raise_for_status()
    except requests.exceptions.RequestException as error_message:
        print(error_message)
        sys.exit(1)

    response_body = api_request.json()

    return response_body


def rubrik_patch(api_version, api_endpoint, config, token):
    """ Connect to a Rubrik Cluster and perform a POST operation """

    AUTHORIZATION_HEADER = {'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'Authorization': 'Bearer ' + token
                            }

    config = json.dumps(config)

    request_url = "https://{}/api/{}{}".format(NODE_IP, api_version, api_endpoint)

    try:
        api_request = requests.patch(request_url, data=config, verify=False, headers=AUTHORIZATION_HEADER)
        # Raise an error if they request was not successful
        api_request.raise_for_status()
    except requests.exceptions.RequestException as error_message:
        print(error_message)
        sys.exit(1)

    response_body = api_request.json()

    return response_body

# Script Specific Function


def get_vm_by_sla_domain(sla_domain_name, token):
    """ """

    sla_domain = rubrik_get('v1', '/sla_domain?name={}'.format(sla_domain_name), token)
    response_data = sla_domain['data']

    for result in response_data:
        try:
            if result['name'] == sla_domain_name:
                sla_domain_id = result['id']
        except:
            continue

    try:
        sla_domain_id
    except NameError:
        print("Error: The Rubrik Cluster does not contain the {} SLA Domain".format(sla_domain_name))
        sys.exit()

    current_vm = rubrik_get('v1', '/vmware/vm?is_relic=false', token)
    response_data = current_vm['data']

    vm_id = []

    for result in response_data:
        try:

            if result['effectiveSlaDomainId'] == sla_domain_id:
                vm_id.append(result['id'])
        except:
            continue

    if bool(vm_id) is False:
        print('\nUnable to locate any virtual machines assigned to the "{}" SLA Domain.\n'.format(sla_domain_name))

    return vm_id


def is_vm_paused(vm_id, action, token):

    data = {}
    data['isVmPaused'] = action

    #print(data)

    response_body = rubrik_patch('v1', '/vmware/vm/{}'.format(vm_id), data, token)

    return response_body


parser = argparse.ArgumentParser()
parser.add_argument('--action', choices=['pause', 'resume'], help='Pause or Resume all scheduled snapshots.')
arguments = parser.parse_args()


if arguments.action == 'pause':
    action = True
elif arguments.action == 'resume':
    action = False
else:
    print('Error: Please use the "--action" flag to specify either "pause" or "resume".')
    sys.exit()


# Variable used to refresh the login token after 30 minutes
REFRESH_TOKEN = 0

# Generate the Initial Login Token
token = login_token(USERNAME, PASSWORD)

if bool(SLA_DOMAIN_NAME_LIST) == False:
    print('Please add at lesat one SLA Domain Name to the SLA_DOMAIN_NAME_LIST variable on line 22.')
    sys.exit()

# Pause all VMs in the SLA Domain
for sla in SLA_DOMAIN_NAME_LIST:
    vm_id_list = get_vm_by_sla_domain(sla, token)

for vm_id in vm_id_list:
    # Crate a new API Token
    if REFRESH_TOKEN == 0:
        token = login_token(USERNAME, PASSWORD)

    is_vm_paused(vm_id, action, token)

    print('Modified {}'.format(vm_id))

    REFRESH_TOKEN += 1

    # After 25 minutes (4500 seconds) reset the Refresh Token
    if REFRESH_TOKEN == 4500:
        REFRESH_TOKEN = 0
=======
#!/usr/bin/env python
# This script comes with no warranty use at your own risk
#
# Title: pause_snapshot
# Author: Drew Russell - Rubrik Ranger Team
# Date: 03/29/2018
# Python ver: 3.6.4
#
# Description:
#
# Pause and Resume a policy driven snapshot of a Virtual Machine

######################################## User Provided Variables #################################


# Cluster IP Address and Credentials
NODE_IP_LIST = []
USERNAME = ""
PASSWORD = ""

# List of SLA Domains to Pause
SLA_DOMAIN_NAME_LIST = []


######################################## End User Provided Variables ##############################

import base64
import asyncio
from aiohttp import ClientSession
import requests
import json
from random import randint
import sys
import argparse
import urllib3


# ignore certificate verification messages
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


parser = argparse.ArgumentParser()
parser.add_argument('--action', choices=['pause', 'resume'], help='Pause or Resume all scheduled snapshots.')
arguments = parser.parse_args()

# Generic Rubrik API Functions


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


async def pause_vm(url):

    node_ip = url.strip('https://').split('/api', 1)[0]
    vm_id = url.split('/vmware/vm/', 1)[-1]

    AUTHORIZATION_HEADER = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Basic ' + basic_auth_header()
    }

    data = {}
    data['isVmPaused'] = ACTION

    data = json.dumps(data)

    async with ClientSession() as session:
        async with session.patch(url, data=data, headers=AUTHORIZATION_HEADER, verify_ssl=False) as response:

            response_body = await response.read()
            try:
                response_body = response_body.decode('utf8').replace("'", '"')
                response_body = json.loads(response_body)
                is_vm_paused = response_body['blackoutWindowStatus']['isSnappableBlackoutActive']
                print(vm_id + ' pause state set to ' + str(is_vm_paused) + ' via Node ' + node_ip)
                VM_MODIFIED.append(vm_id)
            except:
                if response_body['message'] == 'Cannot pause if already paused':
                    print(vm_id + ' pause state set already set to ' + str(ACTION) + ' via Node ' + node_ip)
                    VM_MODIFIED.append(vm_id)
                elif response_body['message'] == 'Cannot resume if not paused':
                    print(vm_id + ' pause state set already set to ' + str(ACTION) + ' via Node ' + node_ip)
                    VM_MODIFIED.append(vm_id)
                else:
                    print(response_body)


def get_vm_by_sla_domain(sla_domain_name):
    """ """
    sla_domain = rubrik_get('v1', '/sla_domain?name={}'.format(sla_domain_name))
    response_data = sla_domain['data']

    for result in response_data:
        try:
            if result['name'] == sla_domain_name:
                sla_domain_id = result['id']
        except:
            continue

    try:
        sla_domain_id
    except NameError:
        print("Error: The Rubrik Cluster does not contain the {} SLA Domain".format(sla_domain_name))
        sys.exit()

    current_vm = rubrik_get('v1', '/vmware/vm?effective_sla_domain_id={}&is_relic=false'.format(sla_domain_id))
    response_data = current_vm['data']

    for result in response_data:
        VM_ID_LIST.append(result['id'])


if arguments.action == 'pause':
    ACTION = True
elif arguments.action == 'resume':
    ACTION = False
else:
    print('Error: Please use the "--action" flag to specify either "pause" or "resume".')
    sys.exit()

NUMBER_OF_NODES = (len(NODE_IP_LIST) - 1)
VM_ID_LIST = []
REQUEST_URL = []
VM_MODIFIED = []

print('Getting VMs for SLA:\n')
for sla in SLA_DOMAIN_NAME_LIST:
    print('  - {}'.format(sla))
    get_vm_by_sla_domain(sla)


print('\nBuilding the API calls....')
for vm_id in VM_ID_LIST:
    api_endpoint = "/vmware/vm/{}".format(vm_id)

    random_list_index = randint(0, NUMBER_OF_NODES)

    node_ip = NODE_IP_LIST[random_list_index]

    REQUEST_URL.append("https://{}/api/{}{}".format(node_ip, 'v1', api_endpoint))


tasks = []
loop = asyncio.get_event_loop()
for url in REQUEST_URL:
    task = asyncio.ensure_future(pause_vm(url))
    tasks.append(task)

print('\nStarting the execution of the API calls....\n')
loop.run_until_complete(asyncio.wait(tasks))
print()
print('Total Number of VMs to Pause/Resume  : {}'.format(len(VM_ID_LIST)))
print('Total Number of VMs Paused/Resumed   : {}'.format(len(VM_MODIFIED)))
>>>>>>> 3cbba5eef094335fbc9ade1dcc30b3a7944beb7e
