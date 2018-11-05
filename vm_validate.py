#!c://Users/peterm/AppData/Local/Programs/Python/Python37-32/python.exe -u

from pyVmomi import vim
from pyvim.connect import SmartConnect, Disconnect, SmartConnectNoSSL
import argparse, rubrik_cdm, urllib3, pprint, sys, time, os
urllib3.disable_warnings()

pp = pprint.PrettyPrinter(indent=4)

# Virtual Machine lookup
def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break
    return obj

parser = argparse.ArgumentParser()
parser.add_argument('--vcenter_fqdn')
parser.add_argument('--vcenter_user')
parser.add_argument('--vcenter_pass')
parser.add_argument('--vm_name')
parser.add_argument('--vm_user')
parser.add_argument('--vm_pass')
parser.add_argument('--rubrik_fqdn')
parser.add_argument('--rubrik_user')
parser.add_argument('--rubrik_pass')
parser.add_argument('--service_check')
args= parser.parse_args()
vc_port = '443'

# Connect to Rubrik
rubrik = rubrik_cdm.Connect(args.rubrik_fqdn, args.rubrik_user, args.rubrik_pass)

# Lookup requested VM and Latest Snapshot on Rubrik
print("Getting VM Information")
try:
  vm = rubrik.get('v1', '/vmware/vm?primary_cluster_id=local&name={}'.format(args.vm_name))
  if vm['total'] == 0:
    print ("VM not found on rubrik cluster at args.rubrik_fqdn")
    exit
  if vm['total'] > 0:
    for vm_item in vm['data']:
      if vm_item['name'] == args.vm_name:
        vm_found = vm_item
  if vm_found is None:
    print ("VM not found on rubrik cluster at args.rubrik_fqdn")
    exit
  ss = rubrik.get('v1', '/vmware/vm/{}'.format(vm_found['id']), timeout=150)['snapshots'][-1]
except:
  print("Problem getting latest snapshot")
  raise

# Live mount snapshot, monitor the operation until the Virtual Machine's OS is running
print("Performing Livemount of {} snapshot from {}".format(vm_found['name'],ss['date']))
try:
  load = {}
  lm = rubrik.post('v1', '/vmware/vm/snapshot/{}/mount'.format(ss['id']), load, timeout=150)
except:
  print("Problem with Livemount request")
  raise
print("Monitor for readiness of Livemount")
try:
  lm_status = 0
  lm_last_status = 0
  while lm_status != 'SUCCEEDED':
    lms = rubrik.get('v1', '/vmware/vm/request/{}'.format(lm['id']), timeout=150)
    lm_status = lms['status']
    if lm_status != lm_last_status and lm_last_status:
      print("Livemount Status changed to {}".format(lm_status))
    lm_last_status = lm_status
    time.sleep(5)
    if lm_status == "FAILURE":
      print("Livemount failed")
      raise
  for index, key in enumerate(lms['links']):
    if key['rel'] == 'result':
      lm_id = key['href'].split('/')[-1]
      print ("Livemount ID is {}".format(lm_id))
except:
  print("Problem with Livemount fulfillment")
  raise
time.sleep(15)
print("Checking for machine availability")
try:
  lm_vm_ready = 0
  while lm_vm_ready == 0:
    lm_vm_status = rubrik.get('v1', '/vmware/vm/snapshot/mount/{}'.format(lm_id), timeout=150)
    lm_vm_ready = lm_vm_status['isReady']
    time.sleep(5)
except:
  print("Problem with machine status")
  raise

print("Machine is running")


# Lookup the live mounted virtual machine name
print("Getting mounted VM Name")
try:
  lm_vm_name = rubrik.get('v1', '/vmware/vm/{}'.format(lm_vm_status['mountedVmId']), timeout=150)['name']
  print("VM Mounted as {}".format(lm_vm_name))
except:
  print("Problem with machine name")
  raise
time.sleep(15)

try:
  # Connect to vCenter
  s = SmartConnectNoSSL(host=args.vcenter_fqdn, user=args.vcenter_user, pwd=args.vcenter_pass, port=vc_port)
except:
  print("Problem with vcenter login")
  raise

try:
  # Establish the vCenter Obj
  content = s.RetrieveContent()
except:
  print("Problem with making content obj")
  raise

try:
  # Assemble Creds
  creds = vim.vm.guest.NamePasswordAuthentication(username=args.vm_user, password=args.vm_pass)
except:
  print("Problem with making auth")
  raise

try:
  # Lookup VM by Name
  vm_obj = get_obj(content, [vim.VirtualMachine], lm_vm_name)
except:
  print("Problem with name lookup")
  raise

try:
  # Establish ProcessMgr Obj
  pm = content.guestOperationsManager.processManager
except:
  print("Problem with process mgr obj")
  raise

time.sleep(15)
  
try:
  # Grab Processes from machine
  pl = pm.ListProcessesInGuest(vm_obj, creds)
except:
  print("Problem with listing processes")
  raise

time.sleep(30)

# Iterate process names to find the --service_check - note there is more info in the hash if you need.
try:
  service = 0
  print("Looking for Service : {} ".format(args.service_check))
  for i in pl:
    if args.service_check == i.name:
      print("{} is available".format(i.name))
      service = i.name
  if service == 0:
    print("Do not see service running : {}".format(args.service_check))
except:
  print("Problem with service dump")
  raise

# Remove the live mount 
print("Removing live mount")
try:
  delete_lm = rubrik.delete('v1', '/vmware/vm/snapshot/mount/{}'.format(lm_id), timeout=150)
except:
  print("Problem with livemount removal")
  raise
  
