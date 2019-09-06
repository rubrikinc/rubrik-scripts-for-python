import urllib2
import json
import base64
import time
import ssl
"""
define our rubrik credentials
"""
RUBRIK_IP='rubrik.demo.com'
RUBRIK_USER='admin'
RUBRIK_PASS='mypassword123!'
"""
define our share details
"""
NAS_HOST_NAME='mynashost'
SHARE_NAME='/usr/share_data'
FILESET_NAME='all_files'
SLA_NAME='Gold'
"""
ignore self-signed certs
"""
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_RUBRIK_URL=("https://"+RUBRIK_IP)

"""
Get SLA Domain ID
"""
request = urllib2.Request(BASE_RUBRIK_URL+"/api/v1/sla_domain?primary_cluster_id=local&name="+SLA_NAME)
base64string = base64.encodestring('%s:%s' % (RUBRIK_USER, RUBRIK_PASS)).replace('\n', '')
request.add_header("Authorization", "Basic %s" % base64string)
result = urllib2.urlopen(request, context=ctx)
SLA_DOMAINS = json.load(result.fp)['data']
SLA_DOMAIN_ID = None
for sla_domain in SLA_DOMAINS:
    if sla_domain['name'] == SLA_NAME:
        SLA_DOMAIN_ID=sla_domain['id']
if not SLA_DOMAIN_ID:
    raise 'SLA Domain not found'
"""
Get Host ID
"""
request = urllib2.Request(BASE_RUBRIK_URL+"/api/v1/host?primary_cluster_id=local&name="+NAS_HOST_NAME)
base64string = base64.encodestring('%s:%s' % (RUBRIK_USER, RUBRIK_PASS)).replace('\n', '')
request.add_header("Authorization", "Basic %s" % base64string)
result = urllib2.urlopen(request, context=ctx)
HOSTS = json.load(result.fp)['data']
HOST_ID = None
for host in HOSTS:
    if host['name'] == NAS_HOST_NAME:
        HOST_ID=host['id']
if not HOST_ID:
    raise 'Host not found'
"""
Get Share ID
"""
request = urllib2.Request(BASE_RUBRIK_URL+"/api/internal/host/share")
base64string = base64.encodestring('%s:%s' % (RUBRIK_USER, RUBRIK_PASS)).replace('\n', '')
request.add_header("Authorization", "Basic %s" % base64string)
result = urllib2.urlopen(request, context=ctx)
SHARES = json.load(result.fp)['data']
SHARE_ID = None
for share in SHARES:
    if (share['exportPoint'] == SHARE_NAME) and (share['hostId'] == HOST_ID):
        SHARE_ID=share['id']
if not SHARE_ID:
    raise 'Share not found'
"""
Get Fileset ID
"""
request = urllib2.Request(BASE_RUBRIK_URL+"/api/v1/fileset?primary_cluster_id=local&host_id="+HOST_ID+"&share_id="+SHARE_ID+"&is_relic=false")
base64string = base64.encodestring('%s:%s' % (RUBRIK_USER, RUBRIK_PASS)).replace('\n', '')
request.add_header("Authorization", "Basic %s" % base64string)
result = urllib2.urlopen(request, context=ctx)
FILESET_ID = json.load(result.fp)['data'][0]['id']
if not FILESET_ID:
    raise 'Fileset not found'
"""
Take Snapshot
"""
PAYLOAD={
    'slaId':SLA_DOMAIN_ID
}
request = urllib2.Request(BASE_RUBRIK_URL+"/api/v1/fileset/"+FILESET_ID+"/snapshot")
base64string = base64.encodestring('%s:%s' % (RUBRIK_USER, RUBRIK_PASS)).replace('\n', '')
request.add_header("Authorization", "Basic %s" % base64string)
result = urllib2.urlopen(request, json.dumps(PAYLOAD), context=ctx)
response = json.load(result.fp)
TASK_ID = response['id']
TASK_STATUS = response['status']
"""
Monitor snapshot to completion
"""
while TASK_STATUS not in ['SUCCEEDED','FAILED','WARNING']:
    time.sleep(5)
    request = urllib2.Request(BASE_RUBRIK_URL+"/api/v1/fileset/request/"+TASK_ID)
    request.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(request, context=ctx)
    TASK_STATUS = json.load(result.fp)['status']
print ("Finished taking snapshot with result "+TASK_STATUS)

