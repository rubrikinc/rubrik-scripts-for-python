#!/usr/bin/env python
# This script comes with no warranty use at your own risk
#
# Title: on_demand_snapshot_by_cluster
# Author: Drew Russell - Rubrik Ranger Team
# Date: 03/14/2018
# Python ver: 3.6.4, 2.7.6
#
# Description:
#
# Create an On-Demand Snapshot for all Virtual Machines in a provided VMware Cluster or SLA Domain

######################################## User Provided Variables #################################


# Cluster IP Address and Credentials
NODE_IP = ""
USERNAME = ""
PASSWORD = ""


### Note: Only populate one of the following lists ###

# List of Clusters
VMWARE_CLUSTER_LIST = [] # Ex. ['cluster01', 'cluster02']

# List of SLA Domains
SLA_DOMAIN_NAME_LIST = [] # Ex. ['Gold', 'Silver']

# On-Demand Snapshot SLA Domain

### Note: If SNAPSHOT_SLA_DOMAIN is not modified (i.e not None), we will use the SLA Domain currently
### assigned to the Virtual Machine
SNAPSHOT_SLA_DOMAIN_NAME = None # Ex. 'Gold


######################################## End User Provided Variables ##############################

import base64
import requests
import json
import sys
import time
from requests.auth import HTTPBasicAuth


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


def rubrik_post(api_version, api_endpoint, config, token):
    """ Connect to a Rubrik Cluster and perform a POST operation """

    AUTHORIZATION_HEADER = {'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'Authorization': 'Bearer ' + token
                            }

    config = json.dumps(config)

    request_url = "https://{}/api/{}{}".format(NODE_IP, api_version, api_endpoint)

    try:
        api_request = requests.post(request_url, data=config, verify=False, headers=AUTHORIZATION_HEADER)
        # Raise an error if they request was not successful
        api_request.raise_for_status()
    except requests.exceptions.RequestException as error_message:
        print(error_message)
        sys.exit(1)

    response_body = api_request.json()

    return response_body


# Script Specific Function


def get_vm_by_cluster(cluster_name, token):
    """Get all Virtual Machines and it's effective SLA Domain ID from a specific cluster """

    current_vm = rubrik_get('v1', '/vmware/vm?is_relic=false', token)
    response_data = current_vm['data']

    vm_sla = {}

    for result in response_data:
        try:
            if result['clusterName'] == cluster_name:
                if result['effectiveSlaDomainId'] != "UNPROTECTED":
                    # {vm_id: sla_domain_id}
                    vm_sla[result['id']] = result['effectiveSlaDomainId']
        except:
            continue

    if bool(vm_sla) is False:
        print('\nUnable to locate any virtual machines in the "{}" Cluster.\n'.format(cluster_name))

    return vm_sla


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

    vm_sla = {}

    for result in response_data:
        try:
            if result['effectiveSlaDomainId'] == sla_domain_id:
                vm_sla[result['id']] = result['effectiveSlaDomainId']
        except:
            continue

    if bool(vm_sla) is False:
        print('\nUnable to locate any virtual machines assigned to the "{}" SLA Domain.\n'.format(sla_domain_name))

    return vm_sla


def get_sla_domain_id(sla_domain_name, token):
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

    return sla_domain_id


def on_demand_snapshot(vm_id, sla_id, token):
    """ Create a On Demand Snapshot """
    on_demand_snapshot_config = {}

    on_demand_snapshot_config['slaId'] = sla_id

    rubrik_post('v1', '/vmware/vm/{}/snapshot'.format(vm_id), on_demand_snapshot_config, token)



# Variable used to refresh the login token after 30 minutes
REFRESH_TOKEN = 0

# Generate the Initial Login Token
token = login_token(USERNAME, PASSWORD)

if bool(VMWARE_CLUSTER_LIST) == False and bool(SLA_DOMAIN_NAME_LIST) == False:
    print('Error: There are no values populated for VMWARE_CLUSTER_LIST or SLA_DOMAIN_NAME')
elif bool(VMWARE_CLUSTER_LIST) == True and bool(SLA_DOMAIN_NAME_LIST) == True:
    print('Error: Both VMWARE_CLUSTER_LIST and SLA_DOMAIN_NAME_LIST are populated. Please only populate one or the other')
elif bool(VMWARE_CLUSTER_LIST) == True:

    for cluster in VMWARE_CLUSTER_LIST:

        vm_to_snapshot = get_vm_by_cluster(cluster, token)

        if bool(SNAPSHOT_SLA_DOMAIN_NAME) == True:
            new_sla_domain_id = get_sla_domain_id(SNAPSHOT_SLA_DOMAIN_NAME, token)

            for virtual_machine_id, sla_domain_id in vm_to_snapshot.items():
                vm_to_snapshot[virtual_machine_id] = new_sla_domain_id

    for virtual_machine_id, sla_domain_id in vm_to_snapshot.items():

        # Crate a new API Token
        if REFRESH_TOKEN == 0:
            token = login_token(USERNAME, PASSWORD)

        on_demand_snapshot(virtual_machine_id, sla_domain_id, token)

        print('On-Demand Snapshot of {}'.format(virtual_machine_id))

        REFRESH_TOKEN += 1
        time.sleep(1)

        # After 25 minutes (4500 seconds) reset the Refresh Token
        if REFRESH_TOKEN == 4500:
            REFRESH_TOKEN = 0

elif bool(SLA_DOMAIN_NAME_LIST) == True:

    for sla in SLA_DOMAIN_NAME_LIST:

        vm_to_snapshot = get_vm_by_sla_domain(sla, token)

        if bool(SNAPSHOT_SLA_DOMAIN_NAME) == True:
            new_sla_domain_id = get_sla_domain_id(SNAPSHOT_SLA_DOMAIN_NAME, token)

            for virtual_machine_id, sla_domain_id in vm_to_snapshot.items():
                vm_to_snapshot[virtual_machine_id] = new_sla_domain_id

    for virtual_machine_id, sla_domain_id in vm_to_snapshot.items():

        # Crate a new API Token
        if REFRESH_TOKEN == 0:
            token = login_token(USERNAME, PASSWORD)

        on_demand_snapshot(virtual_machine_id, sla_domain_id, token)

        print('On-Demand Snapshot of {}'.format(virtual_machine_id))

        REFRESH_TOKEN += 1
        time.sleep(1)

        # After 25 minutes (4500 seconds) reset the Refresh Token
        if REFRESH_TOKEN == 4500:
            REFRESH_TOKEN = 0
