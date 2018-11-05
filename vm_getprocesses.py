from pyVmomi import vim
from pyvim.connect import SmartConnect, Disconnect, SmartConnectNoSSL
import argparse

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
parser.add_argument('--u')
parser.add_argument('--p')
parser.add_argument('--vc')
parser.add_argument('--vm')
parser.add_argument('--vmu')
parser.add_argument('--vmp')
args= parser.parse_args()
vc_port = '443'

# This will connect us to vCenter
s = SmartConnectNoSSL(host=args.vc, user=args.u, pwd=args.p, port=vc_port)

# Establish the vCenter Obj
content = s.RetrieveContent()

# Assemble Creds
creds = vim.vm.guest.NamePasswordAuthentication(username=args.vmu, password=args.vmp)

# Lookup VM by Name
vm_obj = get_obj(content, [vim.VirtualMachine], args.vm)

# Establish ProcessMgr Obj
pm = content.guestOperationsManager.processManager

# Grab Processes from machine
pl = pm.ListProcessesInGuest(vm_obj, creds)

# Print process names - note there is more info in the hash if you need.
for p in pl:
  print (p.name)

