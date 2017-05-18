from RubrikSession import RubrikSession
from getpass import getpass
from requests.utils import quote
import arrow


searching = True

#Ask Initial Questions
mgmt_ip = raw_input("Enter Rubrik MGMT ip: ")
user = raw_input("Enter in Rubrik user: ")
password = getpass("Enter in Rubrik password: ")

#Instantiate RubrikSession
rubrik = RubrikSession(mgmt_ip, user, password)

#Get Host List
print("Obtaining VM List")
VM_LIST = rubrik.get_vm()
vmid = ''

#Ask for host and check for existance
while searching:
    try:
        host_input = raw_input("Please enter in VM Name to Query for Restore: ")
        for host in VM_LIST['data']:
            if host['name'] == host_input:
                print("VM " + host_input + " found and selected.")
                vmid = host['id']
                searching = False
                break
        if searching:
            raise rubrik.RubrikException("Host " + host_input + " not found on Rubrik cluster.")

    except rubrik.RubrikException as e:
        print e
        continue

#Assemble snapshot dictionary from all files for vm
snapshots={}
snapshots_dump = rubrik.get_call('vmware/vm/' + vmid + '/snapshot')
for snap in snapshots_dump['data']:
    snapshots[snap['id']] = snap

#Ask for file query
file_query = raw_input("Please enter file query: ")

#File Query
file_dump = rubrik.get_call('vmware/vm/' + vmid + '/search?path=' + file_query)
file_list = []
counter = 1
for file in file_dump['data']:
    print '    [' + str(counter) + ']  ' + file['path']
    counter += 1
    file_list.append(file['path'])
file_choice = int(raw_input('\nEnter your File Choice : ')) - 1
file_versions = file_dump['data'][file_choice]['fileVersions']

#File Versions
counter = 1
for version in file_versions:
    print '    [' + str(counter) + ']  ' + arrow.get(snapshots[version['snapshotId']]['date']).to('local').format('YYYY-MM-DD HH:mm:ss ZZ')
    counter += 1
version_choice = int(raw_input('\nEnter your Snapshot Choice : ')) - 1
print("DONE")

