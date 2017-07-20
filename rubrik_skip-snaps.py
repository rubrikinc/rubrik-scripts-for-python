
import requests, json, sys, time, threading
from getpass import getpass
from requests.auth import HTTPBasicAuth
from RubrikSession import RubrikSession
import re


if __name__ == '__main__':

    CQLSH_COMMANDS = ""

    #Ask Initial Questions
    rubrik_mgmt_ip = raw_input("Enter Rubrik MGMT ip: ")
    rubrik_user = raw_input("Enter in Rubrik user: ")
    rubrik_password = getpass("Enter in Rubrik password: ")

    #Instantiate Rubrik Session
    rubrik = RubrikSession(rubrik_mgmt_ip, rubrik_user, rubrik_password)

    #Retreive master list of VM's from Rubrik
    VM_MASTER = rubrik.get_vm()

    #Retrieve id of VM
    for vm in VM_MASTER['data']:
        cqlsh_string = re.sub('VirtualMachine:::', '', vm['id'])
        cqlsh_string = "CREATE_VMWARE_SNAPSHOT_" + cqlsh_string
        CQLSH_COMMANDS += 'cqlsh -k sd -e "update job_instance set skip = True where job_id = \'' + cqlsh_string + '\'",' + vm['name'] + '\n'
        print "hello"


    #Write to file
    with open('MASTER.csv', 'w+') as f:
        f.write(CQLSH_COMMANDS)
        f.close()

