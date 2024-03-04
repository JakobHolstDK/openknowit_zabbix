b   import pprint


DOCUMENTATION = '''
'''

EXAMPLES = '''

'''
RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule
import json
import requests

def call_jsonrpc_api(zabbixhost, headers, method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    }
    url = "https://{}/api_jsonrpc.php".format(zabbixhost)
    response = requests.post(url, headers=headers, data=json.dumps(payload), verify=True)
    response.raise_for_status()
    return response.json()



#All about templates
def get_template_id(zabbixhost, zabbixtoken, templatename, full=False):
    failed = False
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {zabbixtoken}"
    }
    method = 'template.get'
    params = {
        'output': 'extend',
        'filter': {
            'name': templatename
        }
    }
    try:
        response = call_jsonrpc_api(zabbixhost, headers, method, params)
    except requests.exceptions.RequestException as e:
        return False
    
    if 'error' in response:
        return False
    
    if response['result']:
        if len(response['result']) == 1:
            if full:
                return response['result'][0]
            else:
                return response['result'][0]['templateid']
        elif len(response['result']) > 1:
            return False
        else:
            return False
    return False

# all about hosts

def get_host_id(zabbixhost, zabbixtoken, hostname, full=False):
    failed = False
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {zabbixtoken}"
    }
    method = 'host.get'
    params = {
        'output': 'extend',
        'filter': {
            'host': hostname
        }
    }
    try:
        response = call_jsonrpc_api(zabbixhost, headers, method, params)
    except requests.exceptions.RequestException as e:
        return False
    
    if 'error' in response:
        return False
    
    if response['result']:
        if len(response['result']) == 1:
            if full:
                return response['result'][0]
            else:
                return response['result'][0]['hostid']
        elif len(response['result']) > 1:
            return False
        else:
            return False
    return False

    
# all about hostgroups

def get_hostgroup_id(zabbixhost, zabbixtoken, hostgroup, full=False):
    failed = False
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {zabbixtoken}"
    }
    method = 'hostgroup.get'
    params = {
        'output': 'extend',
        'filter': {
            'name': hostgroup
        }
    }
    try:
        response = call_jsonrpc_api(zabbixhost, headers, method, params)
    except requests.exceptions.RequestException as e:
        return False
    
    if 'error' in response:
        return False
    
    if response['result']:
        if len(response['result']) == 1:
            myresult = response['result'][0]
            return myresult['groupid']
        elif len(response['result']) > 1:
            return False
        else:
            return False
    return False

def get_hostinterface_id(zabbixhost, zabbixtoken, myhost, full=False):
    hostid = get_host_id(zabbixhost, zabbixtoken, myhost)
    failed = False
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {zabbixtoken}"
    }
    method = 'hostinterface.get'
    params = {
        'output': 'extend',
        'hostids': hostid
    }
    try:
        response = call_jsonrpc_api(zabbixhost, headers, method, params)

    except requests.exceptions.RequestException as e:
        return False
    
    if 'error' in response:
        return False
    
    if response['result']:
        if len(response['result']) == 1:
            if full:
                return response['result'][0]
            else:
                return response['result'][0]['interfaceid']
        elif len(response['result']) > 1:
            return False
        else:
            return False
    return False


def get_proxy_id(zabbixhost, zabbixtoken, proxyname, full=False):
    failed = False
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {zabbixtoken}"
    }
    method = 'proxy.get'
    params = {
        'output': 'extend',
        'filter': {
            'host': proxyname
        }
    }
    try:
        response = call_jsonrpc_api(zabbixhost, headers, method, params)
    except requests.exceptions.RequestException as e:
        return False
    
    if 'error' in response:
        return False
    
    if response['result']:
        if len(response['result']) == 1:
            if full:
                return response['result'][0]
            else:
                return response['result'][0]['proxyid']
        elif len(response['result']) > 1:
            return False
        else:
            return False
    return False






        
        
# all about creating 

def create_host(zabbixhost, zabbixtoken, data):
    main = {
        'default': 1,
        'not_default': 0
    }
    useip = {
        'ipaddress': 1,
        'dns': 0
    }

    port = {
        'default': 10050
    }


    available = {
        'available': 1,
        'unavailable': 0
    }
    types = {
        'agent': 1,
        'snmp': 2,
        'ipmi': 3,
        'jmx': 4
    }
    # First we need to create to know if the host already exists
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {zabbixtoken}"
    }
    hostid = get_host_id( zabbixhost, zabbixtoken, data['hostname'] )

    updatehost = False
    if hostid:
        # we need to update the hostA
        updatehost = True
        hostinterfaceid = get_hostinterface_id(zabbixhost, zabbixtoken, data['hostname'])
    try:
        myhostgroups = data['hostgroups']
    except:
        myhostgroups = []

    hostgroupids = []
    for hostgroup in myhostgroups:
        hostgroupid = get_hostgroup_id(zabbixhost, zabbixtoken, hostgroup)
        if hostgroupid is not None:
            grpdata = { 
                "groupid": hostgroupid
            }
            hostgroupids.append(grpdata)

    # we need the template ids
    templateids = []
    for template in data['templates']:
        templateid = get_template_id(zabbixhost, zabbixtoken, template)
        if templateid is not None:
            tmpdata = {
                "templateid": templateid
            }
            templateids.append(tmpdata)
    
    proxyid = get_proxy_id(zabbixhost, zabbixtoken, data['proxy'] )
    if proxyid is None:
        # We must create the proxy
        method = 'proxy.create'
        params = {
            'host': data['proxy'],
            'status': available['available']
        }
        response = call_jsonrpc_api(zabbixhost, headers, method, params)
        try:
            response = call_jsonrpc_api(zabbixhost, headers, method, params)
        except requests.exceptions.RequestException as e:
            return False, 'ConnectionError'
        if 'error' in response:
            return False, "Error in response"
        proxyid = response['result']['proxyid']
    # check if we have a host interface
    hostinterfaceid = get_hostinterface_id(zabbixhost, zabbixtoken, data['hostname'])

    if hostinterfaceid:
        method = 'hostinterface.update'
        params = {
            'interfaceid': hostinterfaceid,
            'dns': data['hostname'],
            'main': main['default'],
            'port': port['default'],
            'type': types['agent'],
            'useip': useip['dns'],
            'proxy_hostid': proxyid
        }
        response = call_jsonrpc_api(zabbixhost, headers, method, params)
        try:
            response = call_jsonrpc_api(zabbixhost, headers, method, params)
        except requests.exceptions.RequestException as e:
            return False, 'ConnectionError'
        if 'error' in response:
            return False, "Error in response"
        return True, "Host interface updated successfully"
    else:
        print("Creating host interface")
        method = 'hostinterface.create'
        params = {
            'dns': data['hostname'],
            'hostid': hostid,
            'main': main['default'],
            'port': port['default'],
            'type': types['agent'], # 'agent', 'snmp', 'ipmi', 'jmx
            'useip': useip['dns'],
            'proxyids': proxyid
        }
        pprint.pprint(params)
        #response = call_jsonrpc_api(zabbixhost, headers, method, params)
        #pprint.pprint(response)

        #try:
        #    response = call_jsonrpc_api(zabbixhost, headers, method, params)
        #xcept requests.exceptions.RequestException as e:
        #    return False, 'ConnectionError'
        #if 'error' in response:
        #    return False, "Error in response"

    if updatehost:
        method = 'host.update'
        params = {
            'hostid': hostid,
            'groups': hostgroupids,
            'templates': templateids
        }
        response = call_jsonrpc_api(zabbixhost, headers, method, params)

        try:
            response = call_jsonrpc_api(zabbixhost, headers, method, params)
        except requests.exceptions.RequestException as e:
            return False, 'ConnectionError'
        if 'error' in response:
            return False, "Error in response"
        return True, "Host updated successfully"
    else:
        method = 'host.create'
        params = {
            'host': data['hostname'],
            'groups': hostgroupids,
            'templates': templateids
        }

        response = call_jsonrpc_api(zabbixhost, headers, method, params)
        try:
            response = call_jsonrpc_api(zabbixhost, headers, method, params)
            pprint.pprint(response)
        except requests.exceptions.RequestException as e:
            return False, 'ConnectionError'
        if 'error' in response:
            return False, "Error in response"
        return True, "Host created successfully"
    

# all about netbox
def get_netbox_data(netboxhost, netboxtoken, data):
    physical = False
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Token {netboxtoken}"
    }
    url = f"https://{netboxhost}/api/dcim/devices/?name={data['hostname']}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    if response.json()['count'] != 0:
        physical = True
        print("Physical host")
        return response.json()
    else:
        print("Virtual host ??? ")
        url = f"https://{netboxhost}/api/virtualization/virtual-machines/?name={data['hostname']}"
        pprint.pprint(url)
        print("--------------------------")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if response.json()['count'] != 0:
            print("Virtual host")
            return response.json()
        else:
            print("Host not found")
            return False
        
    
    

    print("--------------------------")

    return response.json()

    

def main():
    netboxhost = "netbox.openknowit.com"
    neboxtoken = "24aed26facbd204b5e5395a29efa712adadd2842"
    
    zabbixhost = "zabbix.openknowit.com"
    zabbixtoken = "4244f09b4d3b852f96336fce2a439e747caffee07cab9890d42bcd3f45a431b9"
    task = "create_host"
    params = {
        "hostname": "ignite01",
        "proxy":["Zabbix proxy 03"],
        "hostgroups": ["Linux servers", "Zabbix servers"],
        "templates": [ ]
    }






    if task == 'create_host':
        netboxdata = get_netbox_data(netboxhost, neboxtoken, params)
        if not netboxdata:
            return False
        pprint.pprint(netboxdata)
        print("--------------------------")

        
        result = create_host(zabbixhost, zabbixtoken, params)

    return True

if __name__ == '__main__':
    main()
