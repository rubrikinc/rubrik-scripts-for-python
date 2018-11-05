#!/usr/bin/python
import json
import base64
import requests
requests.packages.urllib3.disable_warnings()
# define our Rubrik connection details
rubrik_ip = 'rubrik.demo.com'
rubrik_user = "admin"
rubrik_pass = "Not@Pa55!"
# define our SQL Server host info
sql_host = 'sqlhost01.demo.com'
sla_domain_name = 'Bronze'


def main():
    token = connectRubrik(rubrik_ip, rubrik_user, rubrik_pass)
    sla_domain_id = getRubrikSlaIdByName(sla_domain_name,rubrik_ip,token)
    host_id = getRubrikHostIdByName(sql_host,rubrik_ip,token)
    protectRubrikSqlHost(host_id,sla_domain_id,rubrik_ip,token)
    print ("All SQL instances running on " + sql_host + " added to the " + sla_domain_name + " SLA domain.")
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

def getAllRubrikSqlInstanceIdByHost(host_id,rubrik_ip,token):
    uri = 'https://'+rubrik_ip+'/api/v1/mssql/instance?primary_cluster_id=local&root_id='+host_id
    headers = {'Content-Type':'application/json', 'Authorization':token}
    r = requests.get(uri, headers=headers, verify=False)
    query_object = json.loads(r.text)
    all_instance_ids = []
    for instance in query_object['data']:
        print ("Found instance named " + instance['name'] + " // " + instance['id'])
        all_instance_ids.append(instance['id'])
    return all_instance_ids

def getRubrikSlaIdByName(sla_domain_name,rubrik_ip,token):
    uri = 'https://'+rubrik_ip+'/api/v1/sla_domain?primary_cluster_id=local&name='+sla_domain_name
    headers = {'Content-Type':'application/json', 'Authorization':token}
    r = requests.get(uri, headers=headers, verify=False)
    query_object = json.loads(r.text)
    for sla_domain in query_object['data']:
        if sla_domain['name'] == sla_domain_name:
            return sla_domain['id']
    return 0

def protectRubrikSqlHost(host_id,sla_domain_id,rubrik_ip,token):
    all_instance_ids = getAllRubrikSqlInstanceIdByHost(host_id,rubrik_ip,token)
    for instance_id in all_instance_ids:
        print("Protecting instance ID "+instance_id)
        uri = 'https://'+rubrik_ip+'/api/v1/mssql/instance/'+instance_id
        headers = {'Content-Type':'application/json', 'Authorization':token, 'Accept': 'application/json'}
        payload = '{"configuredSlaDomainId": "'+str(sla_domain_id)+'"}'
        r = requests.patch(uri, data=payload, headers=headers, verify=False)
        if r.status_code != 200:
            raise ValueError("Something went wrong adding the instance to the given SLA domain")
    return 0


# Start program
if __name__ == "__main__":
   main()