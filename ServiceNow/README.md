# ServiceNOW + Rubrik 5.0.2 24 Hour Compliance

These scripts are intended to be used when the Rubrik ServiceNOW Module cannot be installed into ServiceNOW.

This folder pertains 2 scripts:
    * snow_incident_creation.py
    * 24_compliance_ondemand.py

Both these scripts require the python rubrik_cdm module to be installed and environmental variables defined for authentication. Refer to the Python SDK page for more info. [rubrik-sdk-for-python](https://github.com/rubrikinc/rubrik-sdk-for-python)

## Snow Incident Creation

The script called `snow_incident_creation.py` is intended to scan the new 24 hour compliance report at a set time, and automatically create an incident for each row item found where the status is 'Non-Compliance'.

We need to specify credentials and the serviceNOW instance inside the connection string:

```
conn = Connection.Auth(username='admin', password='rubrik', instance='dev99999', api='JSONv2')
```

This is limited to 1000 items currently, this can be adjusted by changing the `limit` value inside the payload:

```
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
```

## 24 Hour Compliance On-Demand

This script called `24_compliance_ondemand.py` will scan the same report and perform an on-demand snapshot for each item that supports the on-demand snapshot type.