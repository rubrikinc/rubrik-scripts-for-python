#!/usr/bin/env python
# This script comes with no warranty use at your own risk
#
# Author: Drew Russell
# Date: 01/24/2019
# Python ver: 3.6.4
#
# Description:
#
# Using the Rubrk Python SDK, take an on-demand snapshot of a vSphere VM and then wait for its completion.
# See https://rubrik.gitbook.io/rubrik-sdk-for-python/ for additional information on env variables used to Connect
# to the Rubrik cluster.
# Example Usage: python on-demand-snapshot.py --vm demo-vm

import urllib3
import argparse
import rubrik_cdm

# Disable warnings if connecting to a Cluster without a certificatie
urllib3.disable_warnings()

# Create and parse a VM name CLI argument
parser = argparse.ArgumentParser(description="Take an On-Demand Snapshot of a vSphere VM.")
parser.add_argument('--vm', help='The name of there vSphere VM you wish to take an on-demand snapshot of.')
arguments = parser.parse_args()

# Establish a connection to the Rubrik cluster through environment variables
rubrik = rubrik_cdm.Connect()

snapshot = rubrik.on_demand_snapshot(arguments.vm, "vmware")
wait_for_completion = rubrik.job_status(snapshot[0]["links"][0]["href"])

print(wait_for_completion)