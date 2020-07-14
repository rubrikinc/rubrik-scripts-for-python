#!/usr/bin/env python3

# Rubrik Reporting Examples with Python
# Demostrative Script to provide examples when using the Rubrik Reports to report on lots of data
# This is built around CDM 5.1 and some components will not work with 5.2 (specifically events which are now in v1 rather than internal)
# print(report_line) is where most of the data will be displayed to the screen from in multiple locations
# Use report_line to send the required data to where it is required

import rubrik_cdm
import urllib3
import time
import json
urllib3.disable_warnings()

node_ip = "my-rubrik-cluster.com"
api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJI"
report_name = "MSSQL-Protection-Report" # This is the name used to create the custom report if it does not exist - see patch_report_body

table_request = {
    "sortBy": "TaskStatus",
    "sortOrder": "asc",
    "requestFilters": {},
    "limit": 9999
}

patch_report_body = {
    "name": report_name,
    "filters": {
    "dateConfig": {
        "period": "Past30Days" # This can be changed to Past7Days for 7 day period
    },
    "taskType": [
        "Backup",
        "LogBackup",
        "LogArchival",
        "LogShipping"
    ],
    "objectType": [
        "Mssql"
        ]
    },
    "chart0": {
        "id": "chart0",
        "name": "Daily Protection Tasks by Status",
        "chartType": "Donut",
        "attribute": "TaskStatus",
        "measure": "TaskCount"
    },
    "chart1": {
        "id": "chart1",
        "name": "Daily Failed Tasks by Object Name",
        "chartType": "VerticalBar",
        "attribute": "ObjectName",
        "measure": "FailedTaskCount"
    },
    "table": {
        "columns": [
            "TaskStatus",
            "TaskType",
            "ObjectName",
            "ObjectType",
            "Location",
            "SlaDomain",
            "StartTime",
            "EndTime",
            "Duration",
            "DataTransferred",
            "DataStored",
            "NumFilesTransferred",
            "EffectiveThroughput",
            "MissedObjects",
            "FailureReason",
            "SnapshotConsistency",
            "ClusterLocation"
        ]
    }
}

def find_report_id(reports, name):
    return [obj for obj in reports if obj['name']==name]

def report_table_details(reportId):
    return rubrik.post('internal', '/report/{}/table'.format(reportId), table_request)

def get_async_request(id):
    return rubrik.get('internal', '/report/request/{}'.format(id))

def build_data_grid(report_table_id):
    return report_table_details(report_table_id)
    
def createMSSQLReport():
    create_report_body = {
        "name": report_name,
        "reportTemplate": "ProtectionTasksDetails"
    }
    create_report = rubrik.post('internal', '/report', create_report_body)
    edit_report = rubrik.patch('internal', '/report/{}'.format(create_report['id']), patch_report_body)
    refresh_report = rubrik.post('internal', '/report/{}/refresh'.format(create_report['id']), {})
    async_request = get_async_request(refresh_report['id'])
    while((async_request['status'] != "SUCCEEDED") and (async_request['status'] != "FAILED")):
        async_request = get_async_request(refresh_report['id'])
        print('Waitng for Report to Refresh. Status: {}'.format(async_request['status']))
        time.sleep(5)
    return create_report

# Connect to Rubrik and Get All Reports
rubrik = rubrik_cdm.Connect(node_ip, api_token=api_key, enable_logging=False)
reports = rubrik.get('internal', '/report?sort_by=name&sort_order=asc', 60)

# Find MSSQL Report (30 days for all MSSQL Protection Tasks) and SLA Compliance Summary Report IDs
mssql_report = find_report_id(reports['data'], report_name)
sla_complaince_report = find_report_id(reports['data'], "SLA Compliance Summary") 
object_backup_summary = find_report_id(reports['data'], "Object Backup Task Summary") 

### BEGIN: Start Getting MSSQL Protection Tasks

# If report does not exist, create the report using createReport() else set the report ID
if([] == mssql_report):
    mssql_report = createMSSQLReport()
    mssql_report_id = mssql_report['id']
    mssql_report_table = report_table_details(mssql_report_id)
else:
    mssql_report_id = mssql_report[0]['id']
    mssql_report_table = report_table_details(mssql_report_id)

# Get Columns and Data Table from report
mssql_report_table_columns = mssql_report_table['columns']
mssql_report_table_datagrid = mssql_report_table['dataGrid']

# Check if report has more values beyond 9999 (9999 can be adjusted on line 14)
if(mssql_report_table['hasMore']):
    # Keep Getting more data until we have all the report information and append to the Data Table
    while(mssql_report_table['hasMore']):
        table_request['cursor'] = mssql_report_table['cursor']
        mssql_report_table = build_data_grid(mssql_report_id)
        mssql_report_table_datagrid += mssql_report_table['dataGrid']

# For each Report Entry, report Column and Value to the console (This is for demo purposes)
for object in mssql_report_table_datagrid:
    colId = 0
    while(colId < len(mssql_report_table_columns)):
        # Simply print each line from the Report with the corrosponding Column
        # At this point, you can write this information to other locations for use
        report_line = ('{}: {}'.format(mssql_report_table_columns[colId], object[colId]))
        print(report_line)
        colId = colId + 1

### END: This step completes gathering data from the MSSQL Report

### BEGIN: Start Processing the SLA Compliance Summary - Default Report provides last 7 days
table_request = {
    "sortBy": "ObjectName",
    "sortOrder": "asc",
    "requestFilters": {"objectType":"Mssql"},
    "limit": 9999
}
sla_compliance_report_table = report_table_details(sla_complaince_report[0]['id'])
sla_compliance_report_columns = sla_compliance_report_table['columns']
sla_complaince_report_datagrid = sla_compliance_report_table['dataGrid']

if(sla_compliance_report_table['hasMore']):
    while(sla_compliance_report_table['hasMore']):
        table_request['cursor'] = sla_compliance_report_table['cursor']
        sla_compliance_report_table = build_data_grid(sla_complaince_report[0]['id'])
        sla_complaince_report_datagrid += sla_compliance_report_table['dataGrid']

for object in sla_complaince_report_datagrid:
    colId = 0
    while(colId < len(sla_compliance_report_columns)):
        # Simply print each line from the Report with the corrosponding Column
        # At this point, you can write this information to other locations for use
        report_line = ('{}: {}'.format(sla_compliance_report_columns[colId], object[colId]))
        print(report_line)
        colId = colId + 1

### END: This step completes gather data from the SLA Compliance Summary

### BEGIN: Start Gathering the Object Summary and Last Protection Points + Events  - Default Report provides last 7 days

table_request = {
    "sortBy": "ObjectName",
    "sortOrder": "asc",
    "requestFilters": {"objectType":"Mssql"},
    "limit": 9999
}

object_backup_summary_table = report_table_details(object_backup_summary[0]['id'])
object_backup_summary_columns = object_backup_summary_table['columns']
object_backup_summary_datagrid = object_backup_summary_table['dataGrid']

if(object_backup_summary_table['hasMore']):
    while(object_backup_summary_table['hasMore']):
        table_request['cursor'] = object_backup_summary_table['cursor']
        object_backup_summary_table = build_data_grid(sla_complaince_report[0]['id'])
        object_backup_summary_datagrid += object_backup_summary_table['dataGrid']

for object in object_backup_summary_datagrid:
    colId = 0
    while(colId < len(object_backup_summary_columns)):
        # Simply print each line from the Report with the corrosponding Column
        # At this point, you can write this information to other locations for use
        report_line = ('{}: {}'.format(object_backup_summary_columns[colId], object[colId]))
        print(report_line)
        colId = colId + 1

### END: Start Gathering the Object Summary and Last Protection Points + Events

### BEGIN: This step starts gathering the Monitoring Tasks for the Cluster

# Each of these requests will take some time to gether but will provide the current state of objects on the cluster

InProgressTasks = rubrik.get('internal', '/event_series?limit=9999&status=Active&object_type=Mssql', timeout=120)
FailedTasks = rubrik.get('internal', '/event_series?limit=9999&status=Failure&object_type=Mssql', timeout=120)
SuccessTasks = rubrik.get('internal', '/event_series?limit=9999&status=Success&object_type=Mssql', timeout=120)
ScheduledTasks = rubrik.get('internal', '/event_series?limit=9999&status=Queued&object_type=Mssql', timeout=120)

### END: This step completes gathering the Monitoring Tasks for the Cluster

### BEGIN: Using Failed Tasks we can load event and event_series information

# Using Failed Tasks from the previous step process each event
for failure in FailedTasks['data']:
    failedObjectId = failure['objectInfo']['objectId']
    # Get Events for the specific Object
    events = rubrik.get('internal', '/event?object_ids={}'.format(failedObjectId))
    for event in events['data']:
        # Get the Event Series and display the top level failrue message
        eventSeriesId = event['eventSeriesId']
        eventInfo = json.loads(event['eventInfo'])

        print('MSSQL Failure: {} failed due to the following error:'.format(event['objectName']))
        print(eventInfo['message'])
        print('Gathering Event Series Data')
        
        # Grab all Event Series data for the failure event
        eventSeriesData = rubrik.get('internal', '/event_series/{}'.format(eventSeriesId))
        print('Failed Event Series for {}\{}. Start Time: {}, End Time: {}, Duration: {}'
            .format(eventSeriesData['location'], eventSeriesData['objectName'], eventSeriesData['startTime'], eventSeriesData['endTime'], eventSeriesData['duration'] ))
        eventCtr = 1
        # Print each message from the event series
        for eventSeries in eventSeriesData['eventDetailList']:
            eventSeriesMessage = json.loads(eventSeries['eventInfo'])
            print('{}: {}'.format(eventCtr, eventSeriesMessage['message']))
            eventCtr = eventCtr + 1
            
### END: Using Failed Tasks we can load event and event_series information