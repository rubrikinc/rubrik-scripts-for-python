
import requests, json, sys, time, threading
from getpass import getpass
from requests.auth import HTTPBasicAuth


lock = threading.Lock()

class RubrikSession:


    class RubrikException(Exception):

        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return self.msg


    def __init__(self, mgmt_ip, user, password):

        #Prompt for configuration info
        self.mgmt_ip = mgmt_ip
        self.baseurl = "https://" + self.mgmt_ip + "/api/v1/"
        self.user = user
        self.password = password

        #Disable ssl warnings for Requests
        requests.packages.urllib3.disable_warnings()

        #attempt login
        self.token = self.login(self.user, self.password)
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer ' + self.token}


    def login(self, user, password):
        uri  = self.baseurl + "session"
        data = {'username':user,'password':password}
        self.auth = HTTPBasicAuth(user,password)
        try:
            r = requests.post(uri, data=json.dumps(data), verify=False, auth=self.auth)
            r.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            print e
            print "\nFriendly Version:  Connection Error - Are you sure this is a valid Rubrik management IP address?"
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            response = r.json()
            if response.has_key('message'):
                print response['message']
            sys.exit(1)
        response = r.json()
        print "Rubrik connection successful and session established."
        return response['token']


    def register_host(self, hostname):
        uri = self.baseurl + "host"
        data = {'hostname': hostname}
        try:
            r = requests.post(uri, data=json.dumps(data), verify=False, headers=self.headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print e
            response = r.json()
            if response.has_key('message'):
                print response['message']
            raise self.RubrikException("HOST Registration Failed: " + response['message'])
        response = r.json()
        print "Successfully Added HOST:  " + hostname
        return response


    def get_vm(self):
        uri = self.baseurl + 'vmware/vm'
        params = {'limit': 9999}
        try:
            r = requests.get(uri, params=params, verify=False, headers=self.headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print e
            response = r.json()
            if response.has_key('message'):
                print response['message']
            raise self.RubrikException("GET VM failed: " + response['message'])
        response = r.json()
        return response

    def get_vm_details(self, id):
        uri = self.baseurl + 'vmware/vm/' + id
        try:
            r = requests.get(uri, verify=False, headers=self.headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print e
            response = r.json()
            if response.has_key('message'):
                print response['message']
            raise self.RubrikException("GET VM failed: " + response['message'])
        response = r.json()
        return response

    def get_vmdk_details(self, vmdk_id):
        uri = self.baseurl + 'vmware/vm/virtual_disk/' + vmdk_id
        try:
            r = requests.get(uri, verify=False, headers=self.headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print e
            response = r.json()
            if response.has_key('message'):
                print response['message']
            raise self.RubrikException("GET VMDK failed: " + response['message'])
        response = r.json()
        return response

def write_to_file(text):
    lock.acquire()
    try:
        with open('Rubrik_VMDK_Details.csv', 'a') as f:
            f.write(text)
    except IOError:
        f.close()
        "FATAL IO ERROR ADDING LINE FOR VMDK"
        sys.exit(1)
    lock.release()


def add_rubrik_thread(mgmt_ip, user, password, vm_list):

    rubrik = RubrikSession(mgmt_ip, user, password)

    for vm in vm_list:
        if vm['isRelic'] is False:
            print "Processing VMDKs for " + vm['name']

            #Construct Folder Path
            folder_path = ""
            for folder in vm['folderPath']:
                folder_path += '/' + folder['name']

            #Retrieve list of vmdk id's
            vmdk_list = (rubrik.get_vm_details(vm['id'])).get('virtualDiskIds', 'No vmdk found')

            #Retrieve vmdk details and write out line in csv
            for vmdk_id in vmdk_list:
                vmdk_details = rubrik.get_vmdk_details(vmdk_id)

                #Attempt to write line to CSV File
                write_to_file(vm['name'] + ',' + folder_path + ',' + vm['id'] + ',' + vmdk_details['fileName'] + ',' + str(vmdk_details['size']/(1024.0*1024.0)) + ',' + vm['effectiveSlaDomainName'] + ',' + vmdk_id + ',' + str(vmdk_details['excludeFromSnapshots']) + '\n')

    print "\nIt took ", (time.time() - start) / 60, "minutes."


if __name__ == '__main__':


    rubriknodes = []
    VMDK_DICT = []
    start = time.time()
    # Attempt to open CSV file for writing
    try:
        with open('Rubrik_VMDK_Details.csv', 'w+') as f:
            f.write('VM NAME,VM FOLDER,VM ID,VMDK FILENAME,VMDK SIZE - MB,EFFECTIVE SLA DOMAIN,VMDK ID,EXCLUDE\n')
    except IOError:
        print "Error:  Can't seem to open file: rubrik_VMDK_Details.csv"
        sys.exit(1)

    #Ask Initial Questions
    rubrik_user = raw_input("Enter in Rubrik user: ")
    rubrik_password = getpass("Enter in Rubrik password: ")
    nodecount = raw_input("Enter in number of concurrent nodes for execution: ")
    nodecount = int(nodecount)

    #Ask for IP of each node
    for i in range (0, nodecount):
        rubriknodes.append(raw_input("Enter in Rubrik Mgmt IP for Node " + str(i) + ": "))

    #Instantiate Rubrik Session
    rubrik = RubrikSession(rubriknodes[0], rubrik_user, rubrik_password)

    #Retreive master list of VM's from Rubrik
    VM_MASTER = rubrik.get_vm()

    #Split up VM_MASTER into #nodecount pieces and repopulate parent of VM_MASTER
    VM_MASTER = [VM_MASTER['data'][i:i+(len(VM_MASTER['data']) / nodecount)] for i in range(0, len(VM_MASTER['data']), len(VM_MASTER['data']) / nodecount)]

    #Merge Last List if there is a non-divisible remainder
    if len(VM_MASTER) > nodecount:
        VM_MASTER[nodecount-1] = VM_MASTER[nodecount-1] + VM_MASTER[nodecount]
        VM_MASTER.pop(nodecount)

    #Kick off each thread for each sub list
    for i in range(0, nodecount):
        print "Kicking off List for Node " + str(i)
        threading.Thread(target=add_rubrik_thread, kwargs={'mgmt_ip':rubriknodes[i], 'user':rubrik_user, 'password':rubrik_password, 'vm_list': VM_MASTER[i]}).start()
