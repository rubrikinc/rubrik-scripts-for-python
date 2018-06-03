## Assign SLA

### [nutanix_assign_sla.py](https://github.com/rubrik-devops/python-scripts/blob/master/Virtual%20Machine/nutanix_assign_sla.py)

Description: Create an On-Demand Snapshot for all Virtual Machines in a provided VMware Cluster.

#### Example Usage (Line 13-22):

```python
######################################## User Provided Variables #################################

NODE_IP = "172.45.23.65"
USERNAME = "admin"
PASSWORD = "rubrik123"

NUTANIX_VM_NAME = 'demo-vm'
SLA_DOMAIN_NAME = 'Gold'


######################################## End User Provided Variables ##############################
```