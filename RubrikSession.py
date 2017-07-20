import requests, json, sys
from requests.auth import HTTPBasicAuth


class RubrikSession:

    class RubrikException(Exception):

        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return self.msg


    def __init__(self, mgmt_ip, user, password):

        #Prompt for configuration info
        self.mgmt_ip = mgmt_ip
        self.baseurl = "https://" + self.mgmt_ip + "/api/v1/"
        self.internal_baseurl = "https://" + self.mgmt_ip + "/api/internal/"
        self.user = user
        self.password = password

        #Disable ssl warnings for Requests
        requests.packages.urllib3.disable_warnings()

        #attempt login
        self.token = self.login(self.user, self.password)
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer ' + self.token}


    def login(self, user, password):
        uri  = self.baseurl + "session"
        data = {'username':user,'password':password}
        self.auth = HTTPBasicAuth(user,password)
        try:
            r = requests.post(uri, data=json.dumps(data), verify=False, auth=self.auth)
            r.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            print e
            print "\nFriendly Version:  Connection Error - Are you sure this is a valid Rubrik management IP address?"
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            response = r.json()
            if response.has_key('message'):
                print response['message']
            sys.exit(1)
        response = r.json()
        print "Rubrik connection successful and session established."
        return response['token']


    def register_host(self, hostname):
        uri = self.baseurl + "host"
        data = {'hostname': hostname}
        try:
            r = requests.post(uri, data=json.dumps(data), verify=False, headers=self.headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print e
            response = r.json()
            if response.has_key('message'):
                print response['message']
            raise self.RubrikException("HOST Registration Failed: " + response['message'])
        response = r.json()
        print "Successfully Added HOST:  " + hostname
        return response


    def get_all_hosts(self):
        all_hosts = self.get_call("host?primary_cluster_id=local")
        return all_hosts


    def get_vm(self, vm_name=""):
        uri = self.baseurl + 'vmware/vm'

        if vm_name is not None:
            params = {'limit': 9999, 'name': vm_name}
        else:
            params = {'limit': 9999}
        try:
            r = requests.get(uri, params=params, verify=False, headers=self.headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print e
            response = r.json()
            if response.has_key('message'):
                print response['message']
            raise self.RubrikException("GET VM failed: " + response['message'])
        response = r.json()
        return response

    def get_vm_details(self, id):
        uri = self.baseurl + 'vmware/vm/' + id
        try:
            r = requests.get(uri, verify=False, headers=self.headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print e
            response = r.json()
            if response.has_key('message'):
                print response['message']
            raise self.RubrikException("GET VM failed: " + response['message'])
        response = r.json()
        return response

    def get_vmdk_details(self, vmdk_id):
        uri = self.baseurl + 'vmware/vm/virtual_disk/' + vmdk_id
        try:
            r = requests.get(uri, verify=False, headers=self.headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print e
            response = r.json()
            if response.has_key('message'):
                print response['message']
            raise self.RubrikException("GET VMDK failed: " + response['message'])
        response = r.json()
        return response

    def update_vmdk(self, vmdk_id, params):
        uri = self.baseurl + 'vmware/vm/virtual_disk/' + vmdk_id
        try:
            data = params
            r = requests.patch(uri, data=json.dumps(data), verify=False, headers=self.headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print e
            response = r.json()
            if response.has_key('message'):
                print response['message']
            raise self.RubrikException("GET VMDK failed: " + response['message'])
        response = r.json()
        return response

    def get_call(self,call,params={},internal=False):
        if internal:
            uri = self.internal_baseurl + call
        else:
            uri = self.baseurl + call
        try:
            r = requests.get(uri, params=json.dumps(params), verify=False, headers=self.headers)
            r.raise_for_status()
        except requests.RequestException as e:
            print e
            raise self.RubrikException("GET call Failed: " + str(e))
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
            print e
            response = r.json()
            if response.has_key('message'):
                print response['message']
            raise self.RubrikException("Call Failed: " + response['message'])
        response = r.json()
        return response

    def patch_call(self, call, data):
        uri  = self.baseurl + call
        try:
            r = requests.patch(uri, data=data, verify=False, auth=self.auth)
            r.raise_for_status()
        except requests.RequestException as e:
            print e
            raise self.RubrikException("PATCH call failed: " + str(e))
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
            print r
            response = r.json()
            if response.has_key('message'):
                print response['message']
            raise self.RubrikException("Call Failed: " + response['message'])
            sys.exit(1)

    def post_call(self, call, data, internal=False):
        uri  = self.baseurl + call
        if internal:
            uri = self.internal_baseurl + call
        else:
            uri = self.baseurl + call

        try:
            r = requests.post(uri, data=data, verify=False, auth=self.auth)
            r.raise_for_status()
        except requests.RequestException as e:
            print e
            raise self.RubrikException("POST Call Failed: " + str(e))
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
            print e
            response = r.json()
            if response.has_key('message'):
                print response['message']
            raise self.RubrikException("Call Failed: " + response['message'])
            sys.exit(1)

    def delete_call(self,call,params={},internal=False):
        if internal:
            uri = self.internal_baseurl + call
        else:
            uri = self.baseurl + call
        try:
            r = requests.delete(uri, params=json.dumps(params), verify=False, headers=self.headers)
            r.raise_for_status()
        except requests.RequestException as e:
            print e
            raise self.RubrikException("DELETE call Failed: " + str(e))
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
            print e
            response = r.json()
            if response.has_key('message'):
                print response['message']
            raise self.RubrikException("Call Failed: " + response['message'])



    def get_filesets_for_hostid(self, hostid, params):
        fileset_response = self.get_call('fileset', params)
        return fileset_response['data']

    def get_per_vm_storage_list(self):
        per_vm_storage = self.get_call('stats/per_vm_storage', params={}, internal=True)
        return per_vm_storage['data']

    def get_envision_table(self, report_id, params={}):
        table = self.get_call('report/' + report_id + '/table?limit=9999', params=json.dumps(params), internal=True)
        return table

    def take_snapshot(self, vm_id, params={}):
        snapshot = self.post_call('vmware/vm/' + vm_id + '/snapshot', data=json.dumps(params))
        return snapshot

