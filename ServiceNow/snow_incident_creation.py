#!/usr/bin/python3

# SNOW Automatic Incident Creation for 24 Hour Compliance
#
# Requirements: Python3
#               rubrik_cdm module (pip install rubrik_cdm)
#               servicenow module (pip install servicenow)
#               Rubrik CDM 5.0.2+
#               Environment variables for RUBRIK_IP (IP of Rubrik node), RUBRIK_USER (Rubrik username), RUBRIK_PASS (Rubrik password)

from servicenow import ServiceNow
from servicenow import Connection
import rubrik_cdm

conn = Connection.Auth(username='admin', password='rubrik', instance='dev99999', api='JSONv2')

rubrik = rubrik_cdm.Connect()
inc = ServiceNow.Incident(conn)

table_payload = {
    "dataSource":"FrequentDataSource",
    "reportTableRequest":{
        "sortBy":"ObjectName",
        "sortOrder":"asc",
        "requestFilters":{
            "compliance24HourStatus": "NonCompliance"
        },
        "limit":1000
    }
}

events = rubrik.post('internal','/report/data_source/table',table_payload)

for event in events['dataGrid']:

    incident_description = (
        'Object Name: ' + event[13] + '\n' +
        'Location: ' + event[1] + '\n' +
        'Object Type: ' + event[16] + '\n' +
        'SLA Domain Name: ' + event[11] + '\n' +
        'Snapshot Count in last 24 hours: ' + event[2] + '\n' +
        'Snapshot 24hr Compliance: ' + event[9] + '\n' +
        'Last Snapshot: ' + event[10] + '\n' +
        'Latest Archival Snapshot: ' + event[12] + '\n' +
        'Latest Replication Snapshot: ' + event[15] + '\n' +
        'Object State: ' + event[6] + '\n')
    
    incident_shortname = (
        'Failed Backup in last 24 hours Object: ' + event[13] + ' in SLA: ' + event[11]
    )

    incident = {
        'parent': '', 
        'made_sla': '', 
        'caused_by': '', 
        'watch_list': '', 
        'upon_reject': 'cancel', 
        'sys_updated_on': '', 
        'child_incidents': '', 
        'hold_reason': '', 
        'approval_history': '', 
        'resolved_by': '', 
        'sys_updated_by': 'admin',  # change this to not use System Administrator account
        'opened_by': 'Angelo Ferentz',  # Change this to set opened by value
        'user_input': '', 
        'sys_created_on': '2018-08-30 08:06:52', 
        'sys_domain': 'global', 
        'state': '1', 
        'sys_created_by': 'admin',  # change this to not use System Administrator account
        'knowledge': 'false', 
        'order': '', 
        '__status': 'success', 
        'calendar_stc': '', 
        'closed_at': '', 
        'business_duration': '', 
        'group_list': '', 
        'work_end': '', 
        'caller_id': 'Angelo Ferentz', #Update this with the Caller Name
        'reopened_time': '', 
        'resolved_at': '', 
        'approval_set': '', 
        'subcategory': 'ISSUE', 
        'work_notes': '', 
        'short_description': incident_shortname, # Uses the shortname incident description defined earlier in the script
        'close_code': '', 
        'correlation_display': '', 
        'delivery_task': '', 
        'work_start': '', 
        'assignment_group': '', 
        'additional_assignee_list': '', 
        'business_stc': '', 
        'description': '', 
        'calendar_duration': '', 
        'close_notes': '', 
        'notify': '1', 
        'service_offering': '', 
        'sys_class_name': 'incident', 
        'closed_by': '', 
        'follow_up': '', 
        'parent_incident': '', 
        'sys_id': '57af7aec73d423002728660c4cf6a71c', 
        'contact_type': '', 
        'reopened_by': '', 
        'incident_state': 'Assigned', 
        'urgency': '4', # Set priority on incident
        'problem_id': '', 
        'company': '', 
        'reassignment_count': '0', 
        'activity_due': '', 
        'assigned_to': '',  # set this to defined an assigned to group
        'severity': '3', # Sets the severity
        'comments': incident_description, #Sets a description on the incident with the failed backup
        'approval': 'not requested', 
        'sla_due': '', 
        'comments_and_work_notes': '', 
        'due_date': '', 
        'sys_mod_count': '4', 
        'reopen_count': '0', 
        'sys_tags': '', 
        'escalation': '0', 
        'upon_approval': 'proceed', 
        'correlation_id': '', 
        'location': '', 
        'category': 'inquiry'
        }

    inc.create(incident)
