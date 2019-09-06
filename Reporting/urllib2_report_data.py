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
ignore self-signed certs
"""
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
# get the report ID
BASE_RUBRIK_URL=("https://"+RUBRIK_IP)
request = urllib2.Request(BASE_RUBRIK_URL+"/api/internal/report?report_template=ProtectionTasksDetails&report_type=Canned")
base64string = base64.encodestring('%s:%s' % (RUBRIK_USER, RUBRIK_PASS)).replace('\n', '')
request.add_header("Authorization", "Basic %s" % base64string)
result = urllib2.urlopen(request, context=ctx)
REPORT_ID = json.load(result.fp)['data'][0]['id']
# get the report data
PAYLOAD = {
    'requestFilters': {
        'taskType': 'Backup',
        'taskStatus': 'Failed'
    }
}
output = []
HAS_MORE = True
cursor = None
while HAS_MORE:
    # set the cursor if we have one
    if cursor:
        PAYLOAD['cursor'] = cursor
    request = urllib2.Request(BASE_RUBRIK_URL+"/api/internal/report/"+REPORT_ID+"/table")
    base64string = base64.encodestring('%s:%s' % (RUBRIK_USER, RUBRIK_PASS)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    request.add_header('Content-Type', 'application/json')
    result = urllib2.urlopen(request, json.dumps(PAYLOAD), context=ctx)
    REPORT_DATA = json.load(result.fp)
    HAS_MORE = REPORT_DATA['hasMore']
    cursor = REPORT_DATA['cursor']
    for entry in REPORT_DATA['dataGrid']:
        this_entry = {}
        for i in range(len(REPORT_DATA['columns'])):
            this_entry[REPORT_DATA['columns'][i]] = entry[i]
        output.append(this_entry)
