from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect, SmartConnectNoSSL
from getpass import getpass
import re
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
parser.add_argument('--host')
parser.add_argument('--count')
parser.add_argument('--start')
parser.add_argument('--local_ds', action='store_true')
args_list = parser.parse_args()


username = 'marcus.faust@rangers.lab'
password = getpass("Enter in vcenter password: ")


vcenter_ip = 'visa-vcsa.rangers.lab'
vcenter_port = '443'
cluster_name = 'Visa-POC-Cluster'
folder_name = 'Windows-POC'
template_name = 'Win2012R2-template'
customization_spec_name = 'Windows Server 2012R2'
host_name = args_list.host
count = int(args_list.count)
start = int(args_list.start)
new_vm_prefix = 'win'
index=0

# This will connect us to vCenter
s = SmartConnectNoSSL(host=vcenter_ip, user=username, pwd=password, port=vcenter_port)

for i in range(start, (start+count)):

    content = s.RetrieveContent()
    dscluster = get_obj(content, [vim.StoragePod], 'Visa-DS-Cluster')


    # With this we are searching for the MOID of the VM to clone from
    template_vm = get_obj(content, [vim.VirtualMachine], template_name)

    # This gets the MOID of the Guest Customization Spec that is saved in the vCenter DB
    guest_customization_spec = s.content.customizationSpecManager.GetCustomizationSpec(name=customization_spec_name)

    # This will retrieve the Cluster MOID
    cluster = get_obj(content, [vim.ClusterComputeResource], cluster_name)

    host = get_obj(content, [vim.HostSystem], host_name)
    folder = get_obj(content, [vim.Folder], folder_name)
    local_ds_list = []
    for datastore in host.datastore:
        if datastore.name.startswith('esx'):
            local_ds_list.append(datastore)

    # This constructs the reloacate spec needed in a later step by specifying the default resource pool (name=Resource) of the Cluster
    # Alternatively one can specify a custom resource pool inside of a Cluster
    #relocate_spec = vim.vm.RelocateSpec(pool=cluster.resourcePool)
    if args_list.local_ds:

        relocate_spec = vim.vm.RelocateSpec(host=host, datastore=local_ds_list[index])
        cloneSpec = vim.vm.CloneSpec(powerOn=True, template=False, location=relocate_spec, customization=guest_customization_spec.spec)
        clone = template_vm.Clone(name=new_vm_prefix + str(i).zfill(3), folder=folder, spec=cloneSpec)
        print "Built " + new_vm_prefix + str(i).zfill(3)
        index += 1
        continue
    else:


        #relocate_spec = vim.vm.RelocateSpec(host=host)
        relocate_spec = vim.vm.RelocateSpec(pool=cluster.resourcePool)

        # This constructs the clone specification and adds the customization spec and location spec to it
        cloneSpec = vim.vm.CloneSpec(powerOn=True, template=False, location=relocate_spec, customization=guest_customization_spec.spec)

        podsel = vim.storageDrs.PodSelectionSpec()
        podsel.storagePod = dscluster

        storagespec = vim.storageDrs.StoragePlacementSpec()
        storagespec.podSelectionSpec = podsel
        storagespec.vm = template_vm
        storagespec.type = 'clone'
        storagespec.cloneSpec = cloneSpec
        storagespec.cloneName = new_vm_prefix + str(i).zfill(3)
        storagespec.folder = folder


        # Finally this is the clone operation with the relevant specs attached
        #clone = template_vm.Clone(name=new_vm_prefix + '001', folder=template_vm.parent, spec=cloneSpec)

        rec = content.storageResourceManager.RecommendDatastores(storageSpec=storagespec)
        rec_key = rec.recommendations[0].key
        task = content.storageResourceManager.ApplyStorageDrsRecommendation_Task(rec_key)
        print "Built " + new_vm_prefix + str(i).zfill(3)
