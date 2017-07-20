
import requests, json, sys, time, threading
from getpass import getpass
from requests.auth import HTTPBasicAuth
from RubrikSession import RubrikSession



if __name__ == '__main__':


    rubriknodes = []
    VMDK_DICT = []
    start = time.time()
    unprotect_list = []
    dc_id = 'DataCenter:::56868272-f48d-47e0-b16b-0ee86214940f-datacenter-21'
    # Attempt to open CSV file for writing
    try:
        with open('Rubrik_VMDK_Details.csv', 'w+') as f:
            f.write('VM NAME,VM FOLDER,VM ID,VMDK FILENAME,VMDK SIZE - MB,EFFECTIVE SLA DOMAIN,VMDK ID,EXCLUDE\n')
    except IOError:
        print "Error:  Can't seem to open file: rubrik_VMDK_Details.csv"
        sys.exit(1)

    #Ask Initial Questions
    rubrik_mgmt_ip = raw_input("Enter Rubrik MGMT ip: ")
    rubrik_user = raw_input("Enter in Rubrik user: ")
    rubrik_password = getpass("Enter in Rubrik password: ")

    #Instantiate Rubrik Session
    rubrik = RubrikSession(rubrik_mgmt_ip, rubrik_user, rubrik_password)

    #Retreive master list of VM's from Rubrik
    VM_MASTER = rubrik.get_vm()

    #Retrieve list of Folders
    FOLDER_MASTER = rubrik.get_call('folder/vm/' + dc_id, internal=True)
    for folder in FOLDER_MASTER['entities']:
        if folder['entityType'] == 'Folder':
            unprotect_list.append(folder['id'])

    #Assemble Mass UNPROTECT LIST
    #for vm in VM_MASTER['data']:
        #unprotect_list.append(vm['id'])

    #Unprotect entire list
    params = {}
    params['managedIds'] = unprotect_list
    rubrik.post_call(call='sla_domain/INHERIT/assign', data=json.dumps(params), internal=True)
    print ("UNASSIGNED ALL VM's")

    #Delete All Snaps for each VM
    for vm in VM_MASTER['data']:

        #Delete All Snaps
        call = 'vmware/vm/' + vm['id'] + '/snapshot'
        print("Deleting All Snapshots for " + vm['name'])
        rubrik.delete_call(call=call)

