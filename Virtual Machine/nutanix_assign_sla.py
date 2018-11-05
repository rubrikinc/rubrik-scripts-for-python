#!/usr/bin/env python
# This script comes with no warranty use at your own risk
#
# Title: nutanix_assign_sla
# Author: Drew Russell - Rubrik Ranger Team
# Date: 06/03/2018
# Python ver: 3.6.4
#
# Description:
#
# Refresh the Nutanix Cluster and assign an SLA Domain to an AHV VM

######################################## User Provided Variables #################################

NODE_IP = ''
USERNAME = ''
PASSWORD = ''

NUTANIX_VM_NAME = ''
SLA_DOMAIN_NAME = ''

######################################## End User Provided Variables ##############################


import base64
import requests
import json
import sys
import time


# ignore certificate verification messages
requests.packages.urllib3.disable_warnings()


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


def rubrik_job_status(url, timeout=20):
    '''Get the status of a Rubrik job '''

    headers = {
        'Accept': "application/json",
        'Authorization': 'Basic ' + basic_auth_header()
    }

    try:
        api_request = requests.get(url, verify=False, headers=headers)
        # Raise an error if they request was not successful
        api_request.raise_for_status()
    except requests.exceptions.RequestException as error_message:
        print(error_message)
        sys.exit(1)

    response_body = api_request.json()

    return response_body


def rubrik_post(api_version, api_endpoint, config):
    """ Connect to a Rubrik Cluster and perform a POST operation """

    AUTHORIZATION_HEADER = {'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'Authorization': 'Basic ' + basic_auth_header()
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


def rubrik_patch(api_version, api_endpoint, config):
    """ Connect to a Rubrik Cluster and perform a POST operation """

    AUTHORIZATION_HEADER = {'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'Authorization': 'Basic ' + basic_auth_header()
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


def refresh_nutanix_cluster():
    """Refresh the Nutanix Metadata on the Rubrik Cluster """

    current_nutanix_clusters = rubrik_get('internal', '/nutanix/cluster?primary_cluster_id=local')
    response_data = current_nutanix_clusters['data']

    nutanix_cluster_id = []

    for result in response_data:
        nutanix_cluster_id.append(result['id'])

    if not nutanix_cluster_id:
        print('The Rubrik Cluster is currently not connected to any Nutanix Clusters.')
        sys.exit()

    for nutanix_id in nutanix_cluster_id:
        try:
            refresh_nutanix = rubrik_post('internal', '/nutanix/cluster/{}/refresh'.format(nutanix_id), '')

            job_status_link = refresh_nutanix['links'][0]['href']

            # Monitor the status of the Nutanix Refresh and continue once it's complete
            while True:
                refresh_status = rubrik_job_status(job_status_link, timeout=60)

                job_status = refresh_status['status']

                if job_status == "SUCCEEDED":
                    break
                elif job_status == "QUEUED" or "RUNNING":
                    time.sleep(20)
                    continue
                else:
                    print('The Rubrik job failed.')
                    sys.exit()
        except:
            print('Error Unable to refresh {}.'.format(nutanix_id))


def get_nutanix_vm_id():
    """Get the ID of a Nutanix VM """

    nutanix_vm = rubrik_get('internal', '/nutanix/vm?primary_cluster_id=local&name={}'.format(NUTANIX_VM_NAME))

    # Check if any results are returned
    if not nutanix_vm['data']:
        print('There is no Nutanix VM named "{}" on the Rubrik Cluster."'.format(NUTANIX_VM_NAME))
        sys.exit()
    else:
        for vm in nutanix_vm['data']:
            if vm['name'] == NUTANIX_VM_NAME:
                vm_id = vm['id']

    try:
        vm_id
    except NameError:
        print('There is no Nutanix VM named "{}" on the Rubrik Cluster."'.format(NUTANIX_VM_NAME))
        sys.exit()

    return vm_id


def get_sla_domain_id():

    sla_domain = rubrik_get('v1', '/sla_domain?primary_cluster_id=local&name={}'.format(SLA_DOMAIN_NAME))

    # Check if any results are returned
    if not sla_domain['data']:
        print('There is no SLA Domain named "{}" on the Rubrik Cluster.'.format(SLA_DOMAIN_NAME))
        sys.exit()
    else:
        for sla_domain in sla_domain['data']:
            if sla_domain['name'] == SLA_DOMAIN_NAME:
                sla_id = sla_domain['id']

    try:
        sla_id
    except NameError:
        print('There is no SLA Domain named "{}" on the Rubrik Cluster.'.format(SLA_DOMAIN_NAME))
        sys.exit()

    return sla_id


def assign_sla_domain(vm_id, sla_domain_id):

    config = {}
    config['configuredSlaDomainId'] = sla_domain_id

    assign_sla = rubrik_patch('internal', '/nutanix/vm/{}'.format(vm_id), config)


# Refresh the Nutanix Meta Data on the Rubrik Cluster (i.e look for new AHV Virtual Machines)
refresh_nutanix_cluster()

# Get the AHV VM ID and SLA Domain ID
vm_id = get_nutanix_vm_id()
sla_domain_id = get_sla_domain_id()

# Assign the SLA Domain to the AHV VM
assign_sla_domain(vm_id, sla_domain_id)
