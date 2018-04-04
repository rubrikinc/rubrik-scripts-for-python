## On-Demand Snapshots

### [on_demand_snapshot_by_cluster_or_sla.py](https://github.com/rubrik-devops/python-scripts/blob/master/On-Demand%20Snapshot/on_demand_snapshot_by_cluster_or_sla.py)

Description: Create an On-Demand Snapshot for all Virtual Machines in a provided VMware Cluster.

#### Example Usage (Line 185-202):

```python
######################################## User Provided Variables #################################

# Cluster IP Address and Credentials
NODE_IP = "172.45.23.65"
USERNAME = "admin"
PASSWORD = "rubrik123"


### Note: Only populate one of the following lists ###

# List of Clusters
VMWARE_CLUSTER_LIST = [] # Ex. ['cluster01', 'cluster02']

# List of SLA Domains
SLA_DOMAIN_NAME_LIST = [] # Ex. ['Gold', 'Silver']

# On-Demand Snapshot SLA Domain

### Note: If SNAPSHOT_SLA_DOMAIN is not modified (i.e not None), we will use the SLA Domain currently
### assigned to the Virtual Machine
SNAPSHOT_SLA_DOMAIN = None # Ex. 'Gold


######################################## End User Provided Variables ##############################
```

#### Example Output

The _Generic Rubrik API Functions_ (Line 26 to 113) are helper functions utilized in the _Script Specific Funtions_ (Line 114 to 113)  and do not require any modification.

The `get_vm_by_cluster` function will connect to the Rubrik Cluster and utilize the `/vmware/vm` API endpoint to list all Virtual Machines in the Cluster. If the `clusterName` key matches one of the Clusters provided in the `VMWARE_CLUSTER_LIST` variable the fuction will create a dictionary key pair that includes the virtual machine `id` and the `effectiveSlaDomainId` which will then be passed into the `on_demand_snapshot` function.

The `get_vm_by_sla_domain` function will connect to the Rubrik Cluster and utilize the `/sla_domain?name={}` API endpoint to get the SLA Domain ID for the provided SLA Domain Name and then use the `/vmware/vm` API endpoint to list all Virtual Machines in the Cluster. If the `effectiveSlaDomainId` key matches the SLA Domain ID retrived from the previous API call the fuction will create a dictionary key pair that includes the virtual machine `id` and the `effectiveSlaDomainId` which will then be passed into the `on_demand_snapshot` function.


```json
"data": [
    {
      "id": "string",
      "name": "string",
      "configuredSlaDomainId": "string",
      "configuredSlaDomainName": "string",
      "primaryClusterId": "string",
      "slaAssignment": "Derived",
      "effectiveSlaDomainId": "string",
      "effectiveSlaDomainName": "string",
      "effectiveSlaSourceObjectId": "string",
      "effectiveSlaSourceObjectName": "string",
      "moid": "string",
      "vcenterId": "string",
      "hostName": "string",
      "hostId": "string",
      "clusterName": "string",
      "snapshotConsistencyMandate": "UNKNOWN",
      "powerStatus": "string",
      "protectionDate": "2018-03-21T14:03:50.684Z",
      "ipAddress": "string",
      "toolsInstalled": true,
      "isReplicationEnabled": true,
      "folderPath": [
        {
          "id": "string",
          "managedId": "string",
          "name": "string"
        }
      ],
      "infraPath": [
        {
          "id": "string",
          "managedId": "string",
          "name": "string"
        }
      ],
      "vmwareToolsInstalled": true,
      "isRelic": true,
      "guestCredentialAuthorizationStatus": "string",
      "cloudInstantiationSpec": {
        "imageRetentionInSeconds": 0
      }
    }
  ],
```

The following shows the execution of the `get_vm_by_cluster` or `get_vm_by_sla_domain` function which has been modified to show the variables pulled from the Rubrik Cluster. During a normal execution of the script this information will not be visable.

[![asciicast](https://asciinema.org/a/170937.png)](https://asciinema.org/a/170937)

The script will then pass the information pulled from the `get_vm_by_cluster` function into the `on_demand_snapshot` function, which utilizes the `/vmware/vm/{id}/snapshot` endpoint, and create the On-Demand Snapshot. Below is an example of the full output of a production run of the script. Please note that the example has been speed up for the sake of the demostration. It's full funtime is a little over 3 minutes.

[![asciicast](https://asciinema.org/a/170940.png)](https://asciinema.org/a/170940?&speed=3)

Assumptions: This script was created with the goal of creating an On-Demand Backup of 1000's of Virtual Machines at once so a delay of 1 second was added between each backup job. It's also worth noting the `REFRESH_TOKEN` variable which is used to refresh the API token used to authenticate into the Rubrik Cluster before we reach the default timeout value of 30 minuts for the token.