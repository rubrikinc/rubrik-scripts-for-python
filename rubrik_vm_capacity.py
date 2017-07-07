from RubrikSession import RubrikSession
from getpass import getpass
import re
from requests.utils import quote




#Ask Initial Questions
mgmt_ip = raw_input("Enter Rubrik MGMT ip: ")
user = raw_input("Enter in Rubrik user: ")
password = getpass("Enter in Rubrik password: ")
price = raw_input("Enter in price/GB: ")

#Instantiate RubrikSession
rubrik = RubrikSession(mgmt_ip, user, password)

#Get Host List
print("Obtaining VM List")
VM_LIST = rubrik.get_vm()

#Get Per VM Storage Stats
print("Obtaining VM Storage Statistics")
VM_STORAGE = rubrik.get_per_vm_storage_list()

#Create new VM_STORAGE dict keyed on id
VM_STORAGE_ID = {}
for entry in VM_STORAGE:
    id = entry['id']
    VM_STORAGE_ID[id] = {}
    for key in entry:
        VM_STORAGE_ID[id][key] = entry[key]

#Output to CSV
with open('/tmp/MASTER.csv', 'w+') as f:
    f.write('VM NAME,VM FOLDER,VM SLA DOMAIN,LOGICAL GB,INGESTED GB,PHYSICAL GB,$ per LOGICAL GB,$ per INGESTED GB,$ per PHYSICAL GB\n')
    for vm in VM_LIST['data']:
        vm_id = vm['id']
        vm_storage_id = re.sub('VirtualMachine:::','',vm_id)
        path_string = ''
        #Construct Folder Path
        if len(vm['folderPath']) > 0:
            for path in vm['folderPath']:
                path_string += "\\" + path['name']
        else:
            path_string = "\\"
        f.write(vm['name'] + ',' + \
                path_string + ',' + \
                vm['effectiveSlaDomainName'] + ',' + \
                str(float(VM_STORAGE_ID[vm_storage_id]['logicalBytes'])/(1024*1024*1024)) + ',' + \
                str(float(VM_STORAGE_ID[vm_storage_id]['ingestedBytes']) / (1024 * 1024 * 1024)) + ',' + \
                str(float(VM_STORAGE_ID[vm_storage_id]['exclusivePhysicalBytes']) / (1024 * 1024 * 1024)) + ',' + \
                str((float(VM_STORAGE_ID[vm_storage_id]['logicalBytes']) / (1024 * 1024 * 1024)) * float(price)) + ',' + \
                str((float(VM_STORAGE_ID[vm_storage_id]['ingestedBytes']) / (1024 * 1024 * 1024)) * float(price)) + ',' + \
                str((float(VM_STORAGE_ID[vm_storage_id]['exclusivePhysicalBytes']) / (1024 * 1024 * 1024)) * float(price)) + ',' + '\n')
f.close()