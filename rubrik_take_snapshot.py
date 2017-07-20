
import requests, json, sys, time, threading
from getpass import getpass
from requests.auth import HTTPBasicAuth
from RubrikSession import RubrikSession
import argparse




parser = argparse.ArgumentParser()
parser.add_argument('--file')
args_list = parser.parse_args()

file = args_list.file

#Ask Initial Questions
rubrik_mgmt_ip = raw_input("Enter Rubrik MGMT ip: ")
rubrik_user = raw_input("Enter in Rubrik user: ")
rubrik_password = getpass("Enter in Rubrik password: ")

#Instantiate Rubrik Session
rubrik = RubrikSession(rubrik_mgmt_ip, rubrik_user, rubrik_password)

#Retreive master list of VM's from text file
with open(file, 'r') as logfile:
    for line in logfile:

        #Get VM id of VM
        vm_name = line.rstrip("\r\n")
        vm_id = rubrik.get_vm(vm_name)['data'][0]['id']


        #Take On Demand Snapshot
        snapshot = rubrik.take_snapshot(vm_id)
        print "Snapshot initiated for " + vm_name



