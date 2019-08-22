import rubrik_cdm
import urllib3
import csv
import datetime
urllib3.disable_warnings()

rpoInHours = 24
now = datetime.datetime.utcnow()

rubrik = rubrik_cdm.Connect()

fieldnames = ['DatabaseName', 'RootType', 'Location', 'LiveMount', 'Relic', 'BackupDate', 'OutOfCompliance', 'slaAssignment', 'configuredSlaDomainName',
              'copyOnly', 'recoveryModel', 'effectiveSlaDomainName', 'isLogShippingSecondary']

databases = rubrik.get('v1', '/mssql/db', timeout=30)

with open('DatabaseBackupReport.csv', 'w', newline="") as f:
    csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
    csv_writer.writeheader()
    x = 0
    for database in databases["data"]:
        db = rubrik.get('v1', '/mssql/db/{}'.format(database['id']))
        snapshots = rubrik.get('v1', '/mssql/db/{}/snapshot'.format(database['id']))
        complianceStatus = 'Out Of Compliance'
        if len(snapshots['data']) > 0:
            latestSnapshot = datetime.datetime.strptime(snapshots['data'][00]['date'], "%Y-%m-%dT%H:%M:%S.%fZ")
            diff = latestSnapshot - now 
            if (diff.seconds /3600) < rpoInHours:
                complianceStatus = 'Compliant'
            if database['isInAvailabilityGroup'] == True:
                database['recoveryModel'] = 'FULL'

        else:
            latestSnapshot = 'No Snapshot Taken'
        row = {'DatabaseName'               : database['name'],
               'RootType'                   : database['rootProperties']['rootType'],
               'Location'                   : database['rootProperties']['rootName'],
               'LiveMount'                  : database['isLiveMount'],
               'Relic'                      : database['isRelic'],
               'BackupDate'                 : latestSnapshot,
               'OutOfCompliance'            : complianceStatus,
               'slaAssignment'              : database['slaAssignment'],
               'configuredSlaDomainName'    : database['configuredSlaDomainName'],
               'copyOnly'                   : database['copyOnly'],
               'recoveryModel'              : database['recoveryModel'],
               'effectiveSlaDomainName'     : database['effectiveSlaDomainName'],
               'isLogShippingSecondary'     : database['isLogShippingSecondary']}
        print(row)
        csv_writer.writerow(row)
        # x += 1
        # if x == 10:
        #     break