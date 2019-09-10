#!/usr/bin/python3

# Bulk On-Demand Snapshot for 24 Hour Compliance
#
# Requirements: 
#   Python3
#   rubrik_cdm module
#   Rubrik CDM 5.0.2+
#   Environment variables for rubrik_cdm_node_ip (IP of Rubrik node), rubrik_cdm_username (Rubrik username), rubrik_cdm_password (Rubrik password)

import rubrik_cdm
import urllib3
import time

urllib3.disable_warnings()

def RequestStatus(ods_id, obj_type):
    if(obj_type == 'Mssql'):
        endpoint = ('/mssql/request/{}').format(ods_id)
        status = rubrik.get('v1', endpoint)
        print(status)
        return status
    elif(obj_type == 'VmwareVirtualMachine'):
        endpoint = ('/vmware/vm/request/{}').format(ods_id)
        status = rubrik.get('v1',endpoint)
        print(status)
        return status
    elif(obj_type == 'WindowsVolumeGroup'):
        endpoint = ('/vmware/vm/request/{}').format(ods_id)
        status = rubrik.get('v1','/vmware/vm/request/'+ ods_id)
        print(status)
        return status
    elif(obj_type == 'WindowsFileset'):
        endpoint = ('/fileset/request/{}').format(ods_id)
        status = rubrik.get('v1', endpoint)
        print(status)
        return status

def waitForJob(ods_id, obj_type, job_status):
        while job_status not in ['SUCCEEDED', 'FAILED']:
            time.sleep(10)
            job_status = RequestStatus(ods_id, obj_type)
            print('Status of Job is: {}').format(job_status['status'])


debug = 'false'
rubrik = rubrik_cdm.Connect()

table_payload = {
    "dataSource":"FrequentDataSource",
    "reportTableRequest":{
        "sortBy":"ObjectName",
        "sortOrder":"asc",
        "requestFilters":{
            "compliance24HourStatus": "NonCompliance"
        },
        "limit": 5
    }
}

events = rubrik.post('internal','/report/data_source/table',table_payload)
ctr = 0

for event in events['dataGrid']:
    
    ctr = ctr + 1

    object_name = event[13]
    managed_id = event[4]
    sla_domain_id = event[5]
    object_type = event[16]
    sla_name = event[11]

    if (debug == 'false'):

        ods_payload = {
            "slaId": sla_domain_id,
        }

        if (object_type == 'Mssql'):
            
            endpoint = ('/mssql/db/{}/snapshot').format(managed_id)
            api_resp = rubrik.post('v1', endpoint, ods_payload)
            status = RequestStatus(api_resp['id'],object_type)
            waitForJob(status['id'], object_type, status['status'])

        elif (object_type == 'VmwareVirtualMachine'):
            
            endpoint=('/vmware/vm/{}/snapshot').format(managed_id)
            api_resp = rubrik.post('v1', endpoint, ods_payload)
            status = RequestStatus(api_resp['id'],object_type)
            waitForJob(status['id'], object_type, status['status'])

        elif (object_type == 'WindowsVolumeGroup'):

            endpoint=('/volume_group/{}/snapshot').format(managed_id)
            api_resp = rubrik.post('internal', endpoint, ods_payload)
            status = RequestStatus(api_resp['id'],object_type)
            waitForJob(status['id'], object_type, status['status'])

        elif (object_type == 'WindowsFileset'):

            endpoint=('/fileset/{}/snapshot').format(managed_id)
            api_resp = rubrik.post('v1', endpoint, ods_payload)
            status = RequestStatus(api_resp['id'],object_type)
            waitForJob(status['id'], object_type, status['status'])
        
        else:
            print('Unable to perform On-Demand Snapshot for Object Type: ' + object_type)

        api_resp_log = ('On-Demand Snapshot Started for {} (Object Type: {}) using SLA {}').format(object_name, object_type, sla_name)
        print(api_resp_log)

    else:

        print('Object Name: ' + object_name + ', Object Type: ' + object_type)

output_str = ('Script Completed - Started an On-Demand Snpashot for {} Out of Compliance Backups.').format(ctr)
print(output_str)

