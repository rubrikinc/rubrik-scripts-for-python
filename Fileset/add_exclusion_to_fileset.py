<<<<<<< HEAD
#
# Title:        add_exclusion_to_fileset.py
#
# Description:  This script will take all fileset templates of a given type on a Rubrik system, and update the exclusion
#               list to include an array of additional file types.
#
# Author:       Stew Parkin (Assured DP), Tim Hynes (Rubrik)
#

import requests
import json
requests.packages.urllib3.disable_warnings()
## Variables to modify here
username = "admin"
password = "Rubrik123!"
rubrik_ip = "rubrik.demo.com"
excludes = ["*.mp3"]
fileset_type = "SMB"
## Should not need to modify anything beyond this point
clusterUrl = "https://"+rubrik_ip+"/api/v1"
fileseturl = clusterUrl + "/fileset_template?share_type=" + fileset_type
# Get our session token
tokenurl = clusterUrl + "/session"
session = requests.post(tokenurl, verify=False, auth=(username, password))
session = session.json()
token = 'Bearer ' + session['token']
# Get all fileset templates
filesets = requests.get(fileseturl, headers= { 'Accept': 'application/json', 'Authorization': token },verify=False, stream=True)
filesets = filesets.json()
# For each fileset template we will add the new file exclusion types, and patch it using the REST API
for fileset in filesets['data']:
    filesetId = fileset['id']
    for exclude in fileset['excludes']:
        excludes.append(str(exclude))
    data = {"id":filesetId,"excludes":excludes}
    print (data)
    editUrl = clusterUrl+"/fileset_template/"+filesetId
    addExclude = requests.patch(editUrl, data=json.dumps(data), headers= { 'Accept': 'application/json', 'Authorization': token },verify=False, stream=True)
    print addExclude
    print (addExclude.text)
=======
#
# Title:        add_exclusion_to_fileset.py
#
# Description:  This script will take all fileset templates of a given type on a Rubrik system, and update the exclusion
#               list to include an array of additional file types.
#
# Author:       Stew Parkin (Assured DP), Tim Hynes (Rubrik)
#

import requests
import json
requests.packages.urllib3.disable_warnings()
## Variables to modify here
username = "admin"
password = "Rubrik123!"
rubrik_ip = "rubrik.demo.com"
exclude_list = ["*.mp3"]
fileset_type = "SMB"
## Should not need to modify anything beyond this point
clusterUrl = "https://"+rubrik_ip+"/api/v1"
fileseturl = clusterUrl + "/fileset_template?share_type=" + fileset_type
# Get our session token
tokenurl = clusterUrl + "/session"
session = requests.post(tokenurl, verify=False, auth=(username, password))
session = session.json()
token = 'Bearer ' + session['token']
# Get all fileset templates
filesets = requests.get(fileseturl, headers= { 'Accept': 'application/json', 'Authorization': token },verify=False, stream=True)
filesets = filesets.json()
# For each fileset template we will add the new file exclusion types, and patch it using the REST API
for fileset in filesets['data']:
    excludes = exclude_list
    filesetId = fileset['id']
    for exclude in fileset['excludes']:
        excludes.append(str(exclude))
    data = {"id":filesetId,"excludes":excludes}
    print (data)
    editUrl = clusterUrl+"/fileset_template/"+filesetId
    addExclude = requests.patch(editUrl, data=json.dumps(data), headers= { 'Accept': 'application/json', 'Authorization': token },verify=False, stream=True)
    print addExclude
    print (addExclude.text)
>>>>>>> 3cbba5eef094335fbc9ade1dcc30b3a7944beb7e
