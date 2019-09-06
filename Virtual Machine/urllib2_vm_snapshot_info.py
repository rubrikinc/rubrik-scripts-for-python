import urllib2
import json
import base64
import time
import ssl
import argparse
"""
define our rubrik credentials
"""
RUBRIK_IP='rubrik.demo.com'
RUBRIK_USER='admin'
RUBRIK_PASS='mypassword123!'
"""
ignore self-signed certs
"""
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_RUBRIK_URL=("https://"+RUBRIK_IP)
"""
Deal with arguments
"""
parser = argparse.ArgumentParser(description='VM snapshot information')
parser.add_argument('-v', '--vm_name')
args = parser.parse_args()
vm_name = args.vm_name
"""
Get VM ID
"""
request = urllib2.Request(BASE_RUBRIK_URL+"/api/v1/vmware/vm?primary_cluster_id=local&is_relic=false&name="+vm_name)
base64string = base64.encodestring('%s:%s' % (RUBRIK_USER, RUBRIK_PASS)).replace('\n', '')
request.add_header("Authorization", "Basic %s" % base64string)
result = urllib2.urlopen(request, context=ctx)
VM_LIST = json.load(result.fp)['data']
VM_ID = None
for vm in VM_LIST:
    if vm['name'] == vm_name:
        VM_ID=vm['id']
if not VM_ID:
    raise 'VM not found'
"""
Get VM Details
"""
request = urllib2.Request(BASE_RUBRIK_URL+"/api/v1/vmware/vm/"+VM_ID)
base64string = base64.encodestring('%s:%s' % (RUBRIK_USER, RUBRIK_PASS)).replace('\n', '')
request.add_header("Authorization", "Basic %s" % base64string)
result = urllib2.urlopen(request, context=ctx)
response = json.load(result.fp)
SLA_DOMAIN_NAME=response['effectiveSlaDomainName']
NUMBER_OF_SNAPSHOTS=len(response['snapshots'])
LAST_SNAPSHOT_TIME=response['snapshots'][-1]['date']
print ('VM Name: '+vm_name)
print ('SLA Domain: '+SLA_DOMAIN_NAME)
print ('Number of snapshots: '+str(NUMBER_OF_SNAPSHOTS))
print ('Last snapshot: '+LAST_SNAPSHOT_TIME)