#!/usr/bin/env python
# This script comes with no warranty use at your own risk
#
# Title: apply_sla_ec2
# Author: Bill Gurling - Rubrik Ranger Team
# Date: 06/14/2018
#
# Description:
#
# Apply Rubrik EC2 Native Protection SLA to specified EC2 Instances

######################################## User Provided Variables #################################

# Cluster IP Address and Credentials
NODE_IP = ""  # Ex. "se1.rubrikdemo.com"
USERNAME = ""  # Ex. "bill.gurling@rubrik.demo"
PASSWORD = "" #Ex. "Password"

# EC2 Instance Name
EC2_INSTANCE_ID = ""  # Ex. "i-08f31759a24d0ba12"

# SLA DOMAIN NAME
SLA_DOMAIN_NAME = "" #Ex. "EC2 Native DND"

######################################## End User Provided Variables ##############################

import base64
import json
import sys
import time

import requests
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


def rubrik_patch(api_version, api_endpoint, config):
    """ Connect to a Rubrik Cluster and perform a PATCH operation """

    AUTHORIZATION_HEADER = {'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'Authorization': 'Bearer ' + token
                            }

    config = json.dumps(config)

    request_url = "https://{}/api/{}{}".format(
        NODE_IP, api_version, api_endpoint)

    try:
        api_request = requests.patch(
            request_url, data=config, verify=False, headers=AUTHORIZATION_HEADER)
        # Raise an error if they request was not successful
        api_request.raise_for_status()
    except requests.exceptions.RequestException as error_message:
        print(error_message)
        sys.exit(1)

    response_body = api_request.json()

    return response_body


# Script Specific Functions

##get SLA ID from SLA Name
def get_sla_domain_id(sla_domain_name, token):
    """ """

    sla_domain = rubrik_get(
        'v1', '/sla_domain?name={}'.format(sla_domain_name), token)
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
        print("Error: The Rubrik Cluster does not contain the {} SLA Domain".format(
            sla_domain_name))
        sys.exit()
    print(sla_domain_id)
    return sla_domain_id

##get EC2 ID from EC2 Instance Name
def get_ec2_managed_id(aws_instance_id, token):
    """ """

    ec2_managed_instance = rubrik_get(
        'internal', '/aws/ec2_instance?name={}&primary_cluster_id=local'.format(aws_instance_id), token)
    response_data = ec2_managed_instance['data']

    for result in response_data:
        try:
            if result['name'] == aws_instance_id:
                ec2_managed_id = result['id']

        except:
            continue

    try:
        ec2_managed_id
    except NameError:
        print("Error: The Rubrik Cluster does not contain the EC2 Instance {}".format(
            aws_instance_id))
        sys.exit()
    print(ec2_managed_id)
    return ec2_managed_id

##Apply SLA Domain to EC2 Instance
def set_ec2_sla_domain(ec2_managed_id, sla_domain_id, token):

    data_model = {}
    data_model['configuredSlaDomainId'] = sla_domain_id

    response_body = rubrik_patch(
        'internal', '/aws/ec2_instance/{}'.format(ec2_managed_id), data_model)
    
    return response_body
# Generate the Initial Login Token
token = login_token(USERNAME, PASSWORD)

if bool(EC2_INSTANCE_ID) == False and bool(SLA_DOMAIN_NAME) == False:
    print('Error: There is no value populated for EC2_INSTANCE_ID or SLA_DOMAIN_NAME')
elif bool(EC2_INSTANCE_ID) == True and bool(SLA_DOMAIN_NAME) == False:
    print('Error: There is no value populated for SLA_DOMAIN_NAME')
elif bool(EC2_INSTANCE_ID) == False and bool(SLA_DOMAIN_NAME) == True:
    print('Error: There is no value populated for EC2_INSTANCE_ID')
else:
    sla_domain_id = get_sla_domain_id(SLA_DOMAIN_NAME, token)
    ec2_managed_id = get_ec2_managed_id(EC2_INSTANCE_ID, token)
    set_ec2_sla_domain(ec2_managed_id,sla_domain_id, token)
