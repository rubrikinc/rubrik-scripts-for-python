from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect, SmartConnectNoSSL
from getpass import getpass
import argparse




def get_obj(content, vimtype, name):
    """
    Return an object by name, if name is None the
    first found object is returned
    """
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
parser.add_argument('--folder')
args_list = parser.parse_args()


username = 'marcus.faust@rangers.lab'
password = getpass("Enter in vcenter password: ")
vcenter_ip = 'visa-vcsa.rangers.lab'
vcenter_port = '443'
cluster_name = 'Visa-POC-Cluster'
folder_name = args_list.folder
template_name = 'Centos7-Throughput'
customization_spec_name = 'Centos7-spec'
new_vm_prefix = 'linTP'

# This will connect us to vCenter
s = SmartConnectNoSSL(host=vcenter_ip, user=username, pwd=password, port=vcenter_port)

content = s.RetrieveContent()

#Get Folder
folder = get_obj(content, [vim.Folder], folder_name)

#Reboot Each VM
for vm in folder.childEntity:
    print "Rebooting " + vm.name
    vm.RebootGuest()

