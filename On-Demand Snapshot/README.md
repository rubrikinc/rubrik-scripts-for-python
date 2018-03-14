## On-Demand Snapshots

#### [on_demand_snapshot_by_cluster.py](https://github.com/rubrik-devops/python-scripts/blob/master/On-Demand%20Snapshot/on_demand_snapshot_by_cluster.py)

Description: Create an On-Demand Snapshot for all Virtual Machines in a provided VMware Cluster.

Example Usage (Line 149-155):

```
# Cluster IP Address and Credentials
NODE_IP = "172.58.62.123"
USERNAME = "demo"
PASSWORD = "rubrik"

# List of Clusters
CLUSTER_LIST = ['cluster01', 'cluster02]
```

Assumptions: This script was created with the goal of creating an On-Demand Backup of 1000's of Virtual Machines at once so a delay of 1 second was added between each backup job.