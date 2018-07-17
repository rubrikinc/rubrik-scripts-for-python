#!/usr/bin/env python

import rubrik, argparse, requests, json, logging, time, sys
from datetime import datetime, timedelta, timezone

# Gather parameters
parser = argparse.ArgumentParser(description='Recover Linux system to another running Linux system.')
parser.add_argument('-c', '--confirm', dest='confirm', action='store_true', required=False,
                    help='Perform restore without asking for confirmation.')
parser.add_argument('-d', '--destinationpath', dest='path', required=True,
                    help='Path on the destination to recover conflicting files to.')
parser.add_argument('-D', '--debug', dest='debug', action='store_true', required=False,
                    help='Debug output.')
parser.add_argument('-n', '--node', dest='node_ip', required=True,
                    help='IP Address or FQDN of node in Rubrik Cluster')
parser.add_argument('-p', '--password', dest='password', required=True,
                    help='Password on the Rubrik Cluster Rubrik Cluster')
parser.add_argument('-s', '--sourcehost', dest='source_hostname', required=True,
                    help='The hostname of the source system being recovered. ATTENTION!!! An exact match is required to proceed.')
parser.add_argument('-t', '--targethost', dest='target_hostname', required=True,
                    help='The hostname of the target system being recovered to. ATTENTION!!! An exact match is required to proceed.')
parser.add_argument('-u', '--username', dest='username', required=True,
                    help='Username on the Rubrik Cluster')

args = parser.parse_args()
node_ip = args.node_ip
username = args.username
password = args.password
source_hostname = args.source_hostname
target_hostname = args.target_hostname
path = args.path
confirm = args.confirm
debug = args.debug

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler(__file__ + '.' + source_hostname + '.log', mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger

def export_dir(sourcedir,destinationdir,snapshotid):

    config = {
        "sourceDir": sourcedir,
        "destinationDir": destinationdir,
        "ignoreErrors": True,
        "hostId": target_host['data'][0]['id']
    }

    result = rubrik.post('v1', '/fileset/snapshot/{}/export_file'.format(snapshotid), config)
    return(result)

def get_job_status(req_id):
    global result_status
    result_status = ""
    waiting = True
    logger.info ('Checking on job status of {}...'.format(req_id))
    while waiting is True:
        time.sleep(10)
        status_check = rubrik.get('v1', '/fileset/request/{}'.format(req_id))
        waiting = False
        job_status = status_check['status']
        result_status = status_check
        if job_status not in ['SUCCEEDED','FAILED']:
            status_str = "JOB STATUS for {}: {}, PROGRESS: {}".format(req_id, job_status, status_check['progress'])
            waiting = True
        else:
            status_str = "JOB STATUS for {}: {}".format(req_id, job_status)
        logger.info (status_str)
    #debug(result_status)
    logger.info ("Operation Complete: {}".format(result_status['status']))

# Enable logging
logger = setup_custom_logger('file-restore')

# ignore certificate verification messages
requests.packages.urllib3.disable_warnings()

# Connect to the Rubrik Cluster.
logger.info ('')
logger.info ('Connecting to Rubrik cluster node {}...'.format(node_ip))
rubrik = rubrik.Connect(node_ip, username, password)

# Grab source host info
config = {
    "hostname": source_hostname
}
source_host = rubrik.get('v1', '/host?hostname={}'.format(source_hostname))
target_host = rubrik.get('v1', '/host?hostname={}'.format(target_hostname))

# Grab file set info
config = {
    "host_id": source_host['data'][0]['id']
}
filesets = rubrik.get('v1', '/fileset?host_id={0}&name={1}'.format(source_host['data'][0]['id'],'&name=lnx-base'))
index = 1
logger.info ('')
logger.info ('Available filesets:')
logger.info ('')
for fileset in filesets['data']:
    logger.info ('{0}: {1}'.format(index, fileset['name']))
    index += 1
logger.info ('')
response = None
while response is None:
  response = int(input("Which fileset do you want to recover from? "))

response -= 1

fileset = filesets['data'][response]
logger.info ('')
logger.info ('You selected the fileset from: {}'.format(fileset['name']))
if debug:
    logger.debug (json.dumps(fileset, indent=4, sort_keys=True))
logger.info('')

# List snapshots for user selected fileset
logger.info ('Looking for snapshots of {}...'.format(source_hostname))
fileset_snapshots = rubrik.get('v1', '/fileset/{}'.format(fileset['id']))

index = 1
logger.info ('')
logger.info ('Available snapshots:')
logger.info ('')
snapshots = fileset_snapshots['snapshots']
for snapshot in snapshots:
    logger.info ('{0}: {1}'.format(index, snapshot['date']))
    index += 1
logger.info ('')
response = None
while response is None:
  response = int(input("Which snapshot do you want to recover? "))

response -= 1

snapshot = snapshots[response]
logger.info ('')
logger.info ('You selected the snapshot from: {} '.format(snapshot['date']))
if debug:
    logger.debug (json.dumps(snapshot, indent=4, sort_keys=True))
logger.info ('')

#Restore main set of data
if not confirm:
    response = None
    while response not in ['y','n','Y','N']:
        response = input("Do you want to restore files snapshot of {} from {} to {}? [y/n][Y,N] ".format(source_hostname,snapshot['date'],target_hostname))

    if response in [ 'n', 'N' ]:
        logger.info ('Canceled by user')
        exit ()

export_ids = list()
for directory in "/etc", "/dev/mapper", "/home", "/usr", "/root":
    export = export_dir(directory,directory,snapshot['id'])
    export_ids.append(export['id'])
    logger.info ('Started export of {0} to {0} with export id {1}.'.format(directory,export['id']))

#Restore relocated data
for directory in "/usr",:
    export = export_dir(directory,path,snapshot['id'])
    export_ids.append(export['id'])
    logger.info ('Started export of {} to {} with export id of {}.'.format(directory,path,export['id']))


for export_id in export_ids:
    get_job_status(export_id)

logger.info ('')
logger.info ('Restore operations complete. SSH to {} and run "/bin/cp -rn {} /usr/* /usr; init 6" to complete'.format(target_hostname,path)) 
logger.info ('')
