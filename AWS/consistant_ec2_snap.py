#!/usr/bin/env python

import rubrik
import boto3
import pymongo
import json
import urllib.request


secrets_json_path = './secrets.json'

with open(secrets_json_path) as data:
	secret_data = json.load(data)

node_ip = secret_data['node_ip']
username = secret_data['username']
password = secret_data['password']

# establish a connection to the database
connection = pymongo.MongoClient("mongodb://localhost")

# quiesce the database
result = connection.fsync()

# Connect to the Rubrik Cluster.
rubrik = rubrik.Connect(node_ip, username, password)

# connect to ec2
ec2 = boto3.resource('ec2')

# discover and snapshot the instance
instanceid = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read().decode()
ec2_instance = ec2.Instance(instanceid)
for tag in ec2_instance.tags:
    if tag["Key"] == 'rk_sla':
        rk_sla_name = tag["Value"]

rk_sla = rubrik.get('v1', '/sla_domain?name={}'.format(rk_sla_name))
rk_instance = rubrik.get('internal', '/aws/ec2_instance?name={}'.format(instanceid))

config = {
        "slaId": rk_sla['id']
    }

rk_snapshot = rubrik.post('internal', '/aws/ec2_instance/{}/snapshot'.format(rk_instance['id']), config)

# release the database
result = connection.unlock()

# tag the ami
tag = ec2.Tag(rk_snapshot['imageId'],'amiCustomTag1', 'amiICustomValue1')
respose = tag.load()
tag = ec2.Tag(rk_snapshot['imageId'],'amiCustomTag2', 'amiCustomValue2')
respose = tag.load()
tag = ec2.Tag(rk_snapshot['imageId'],'amiCustomTag3', 'amiCustomValue3')
respose = tag.load()

# tag the snapshots
for snapshot_volume in rk_snapshot['snapshotVolumeIds']:
    tag = ec2.Tag(snapshot_volume, 'snapshotVolumeCustomTag1', 'snapshotVolumeCustomValue1')
    response = tag.load()
    tag = ec2.Tag(snapshot_volume, 'snapshotVolumeCustomTag2', 'snapshotVolumeCustomValue2')
    response = tag.load()
    tag = ec2.Tag(snapshot_volume, 'snapshotVolumeCustomTag3', 'snapshotVolumeCustomValue3')
    response = tag.load()
