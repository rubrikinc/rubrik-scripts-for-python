#!/usr/bin/python3

# Bulk On-Demand Snapshot for 24 Hour Compliance
#
# Requirements: Python 2.7
#               rubrik_cdm module
#               Rubrik CDM 3.0+
#               Environment variables for RUBRIK_IP (IP of Rubrik node), RUBRIK_USER (Rubrik username), RUBRIK_PASS (Rubrik password)

import rubrik_cdm
import urllib3
urllib3.disable_warnings()

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
        "limit": 1000
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

            api_resp = rubrik.post('v1','/mssql/db/' + managed_id + '/snapshot',ods_payload)

        elif (object_type == 'VmwareVirtualMachine'):

            api_resp = rubrik.post('v1','/vmware/vm/' + managed_id + '/snapshot',ods_payload)

        elif (object_type == 'WindowsVolumeGroup'):

            api_resp = rubrik.post('internal','/volume_group/' + managed_id + '/snapshot',ods_payload)

        elif (object_type == 'WindowsFileset'):

            api_resp = rubrik.post('v1','/fileset/' + managed_id + '/snapshot',ods_payload)
        
        else:
            print('Unable to perform On-Demand Snapshot for Object Type: ' + object_type)

        api_resp_log = ('On-Demand Snapshot Started for {} (Object Type: {}) using SLA {}').format(object_name, object_type, sla_name)
        print(api_resp_log)

    else:

        print('Object Name: ' + object_name + ', Object Type: ' + object_type)

output_str = ('Script Completed - Started an On-Demand Snpashot for {} Out of Compliance Backups.').format(ctr)
print(output_str)