""" 
Python Script to download the CSV file from a report within Rubrik CDM
define: 
    cluster - Rubrik CDM IP or Clustername
    api_token - secure token from CDM (username --> API Token manager within the UI)
    download path - path you like to store the file
     report_name - Name of the report from which the CSV will be downloaded
Once set use a cron or task scheduler to run this python script 
"""

# Import modules
import rubrik_cdm
import urllib3
import datetime as dt
import os

# Disable certificate warnings and connect to Rubrik Cluster
urllib3.disable_warnings()

# Parameters used in the script
# Change these to your values 
cluster = "[CLUSTER NAME / IP]"
api_token = "[TOKEN]"
download_path = "/path_name/"
report_name = "Report Name"

# connect to the cluster
rubrik=rubrik_cdm.Connect(cluster, api_token=api_token)

# Find the ID of the report
report = rubrik.get('internal', '/report?name='+report_name)
data = report.get('data')
report_data = {}
for i in data:
    report_data.update(i)
report_id = report_data.get('id')
print(f'The report ID for {report_name} is {report_id} \n')

# Curl example from rubrik to get event
# curl -X GET "https://[CLUSTER]/api/internal/report/[REPORT_ID]/csv_link"
url = rubrik.get('internal', '/report/'+report_id+'/csv_link',timeout=60)

# Download the file and save in os.chdir
# make sure you have wget installed, on Mac run "brew install wget"
os.chdir(download_path)
os.system('wget --no-check-certificate ' + url)
