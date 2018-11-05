#!/usr/bin/python
import json
import base64
import requests
requests.packages.urllib3.disable_warnings()
# define our Rubrik connection details
rubrik_ip = 'rubrik.demo.com'
rubrik_user = "admin"
rubrik_pass = "Not@Pa55!"
# define our SQL Server host/DB info
sql_host = 'sqlhost01.demo.com'
sql_instance = 'WINGTIPTOYS'
sql_db_name = 'CustomerDB'
sla_domain_name = 'Bronze'


def main():
    token = connectRubrik(rubrik_ip, rubrik_user, rubrik_pass)
    sla_domain_id = getRubrikSlaIdByName(sla_domain_name,rubrik_ip,token)
    host_id = getRubrikHostIdByName(sql_host,rubrik_ip,token)
    instance_id = getRubrikSqlInstanceIdByName(host_id,sql_instance,rubrik_ip,token)
    sql_db_id = getRubrikSqlDbIdByName(instance_id,sql_db_name,rubrik_ip,token)
    protectRubrikSqlDb(sql_db_id,sla_domain_id,rubrik_ip,token)
    print (sql_db_name + " running on " + sql_host + "/" + sql_instance + " added to the " + sla_domain_name + " SLA domain.")
    return 0

def connectRubrik(rubrik_ip, rubrik_user, rubrik_pass):
    uri = 'https://'+rubrik_ip+'/api/v1/session'
    b64auth = "Basic "+ base64.b64encode(rubrik_user+":"+rubrik_pass)
    headers = {'Content-Type':'application/json', 'Authorization':b64auth}
    payload = '{"username":"'+rubrik_user+'","password":"'+rubrik_pass+'"}'
    r = requests.post(uri, headers=headers, verify=False, data=payload)
    if r.status_code == 422:
        raise ValueError("Something went wrong authenticating with the Rubrik cluster")
    token = str(json.loads(r.text)["token"])
    return ("Bearer "+token)

def getRubrikHostIdByName(host_name,rubrik_ip,token):
    uri = 'https://'+rubrik_ip+'/api/v1/host?primary_cluster_id=local&hostname='+host_name
    headers = {'Content-Type':'application/json', 'Authorization':token}
    r = requests.get(uri, headers=headers, verify=False)
    query_object = json.loads(r.text)
    for host in query_object['data']:
        if host['hostname'] == host_name:
            return host['id']
    return 0

def getRubrikSqlInstanceIdByName(host_id,instance_name,rubrik_ip,token):
    uri = 'https://'+rubrik_ip+'/api/v1/mssql/instance?primary_cluster_id=local&root_id='+host_id
    headers = {'Content-Type':'application/json', 'Authorization':token}
    r = requests.get(uri, headers=headers, verify=False)
    query_object = json.loads(r.text)
    for instance in query_object['data']:
        if instance['name'] == instance_name:
            return instance['id']
    return 0

def getRubrikSqlDbIdByName(instance_id,db_name,rubrik_ip,token):
    uri = 'https://'+rubrik_ip+'/api/v1/mssql/db?primary_cluster_id=local&instance_id='+instance_id
    headers = {'Content-Type':'application/json', 'Authorization':token}
    r = requests.get(uri, headers=headers, verify=False)
    query_object = json.loads(r.text)
    for sqldb in query_object['data']:
        if sqldb['name'] == db_name:
            return sqldb['id']
    return 0

def getRubrikSlaIdByName(sla_domain_name,rubrik_ip,token):
    uri = 'https://'+rubrik_ip+'/api/v1/sla_domain?primary_cluster_id=local&name='+sla_domain_name
    headers = {'Content-Type':'application/json', 'Authorization':token}
    r = requests.get(uri, headers=headers, verify=False)
    query_object = json.loads(r.text)
    for sla_domain in query_object['data']:
        if sla_domain['name'] == sla_domain_name:
            return sla_domain['id']
    return 0

def protectRubrikSqlDb(sql_db_id,sla_domain_id,rubrik_ip,token):
    uri = 'https://'+rubrik_ip+'/api/v1/mssql/db/'+sql_db_id
    headers = {'Content-Type':'application/json', 'Authorization':token, 'Accept': 'application/json'}
    payload = '{"configuredSlaDomainId": "'+str(sla_domain_id)+'"}'
    r = requests.patch(uri, data=payload, headers=headers, verify=False)
    if r.status_code != 200:
        raise ValueError("Something went wrong adding the database to the given SLA domain")
    return 0

# Start program
if __name__ == "__main__":
   main()