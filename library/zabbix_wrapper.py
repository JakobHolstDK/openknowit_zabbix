import pprint
DOCUMENTATION = '''
'''
EXAMPLES = '''
'''
RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule
import json
import requests

def call_jsonrpc_api(hostname, headers, method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    }
    url = "https://{}/api_jsonrpc.php".format(hostname)
    response = requests.post(url, headers=headers, data=json.dumps(payload), verify=True)
    response.raise_for_status()
    return response.json()

def zabbix_host_id_get(module, hostname, token, data):
    failed = False
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {token}"
    }
    method = 'host.get'
    params = {
        'output': 'extend',
        'filter': {
            'host': data['hostname']
        }
    }
    try:
        response = call_jsonrpc_api(hostname, headers, method, params)
    except requests.exceptions.RequestException as e:
        return False
    
    if 'error' in response:
        return False
    
    if response['result']:
        if len(response['result']) == 1:
            myresult = response['result'][0]
            return myresult
        elif len(response['result']) > 1:
            return False
        else:
            return False
    return False

def zabbix_host_get(module, hostname, token, data):
    failed = False
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {token}"
    }
    method = 'host.get'
    params = {
        'output': 'extend',
        'filter': {
            'host': data['hostname']
        }
    }
    try:
        response = call_jsonrpc_api(hostname, headers, method, params)
    except requests.exceptions.RequestException as e:
        failed=True
        module.fail_json(msg=f"Failed to call Zabbix API: response: {response}   )  ")

    if 'error' in response:
        error = response['error']
        module.fail_json(msg=f"Zabbix API call failed: {error['message']}",
                         error_code=error['code'],
                         error_data=error.get('data'))
    if response['result']:
        if len(response['result']) == 1:
            myresult = response['result'][0]
            module.exit_json(changed=False, result=myresult)
            return myresult
        elif len(response['result']) > 1:
            module.fail_json(msg=f"Found more than one host with the name: {data['hostname']}")
            return False
        else:
            module.exit_json(changed=False, result="Host not found")
            return False
        
def get_hostgroup_id(hostname, token, data):
    failed = False
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {token}"
    }
    method = 'hostgroup.get'
    params = {
        'output': 'extend',
        'filter': {
            'name': data['hostgroup']
        }
    }
    try:
        response = call_jsonrpc_api(hostname, headers, method, params)
    except requests.exceptions.RequestException as e:
        return False
    
    if 'error' in response:
        return False
    
    if response['result']:
        if len(response['result']) == 1:
            myresult = response['result'][0]
            return myresult
        elif len(response['result']) > 1:
            return False
        else:
            return False
    return False
        
        
def get_hostgroup(module, hostname, token, data):
    failed = False
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {token}"
    }
    method = 'hostgroup.get'
    params = {
        'output': 'extend',
        'filter': {
            'name': data['hostgroup']
        }
    }
    try:
        response = call_jsonrpc_api(hostname, headers, method, params)
    except requests.exceptions.RequestException as e:
        failed=True
        module.fail_json(msg=f"Failed to call Zabbix API: response: {response}   )  ")

    if 'error' in response:
        error = response['error']
        module.fail_json(msg=f"Zabbix API call failed: {error['message']}",
                         error_code=error['code'],
                         error_data=error.get('data'))
    if response['result']:
        if len(response['result']) == 1:
            myresult = response['result'][0]
            module.exit_json(changed=False, result=myresult)
            return myresult
        elif len(response['result']) > 1:
            module.fail_json(msg=f"Found more than one host with the name: {data['hostname']}")
            return False
        else:
            module.exit_json(changed=False, result="Host not found")
            return False
        

        
def zabbix_host_update(module, hostname, token, data):
    failed = False
    # To be implemented

    return True




def zabbix_host_create(module, hostname, token, data):
    # First we need to create to know if the host already exists
    hostid = zabbix_host_id_get(module, hostname, token, data)
    if hostid:
        module.exit_json(changed=False, result="Host already exists")
        zabbix_host_update(module, hostname, token, data)
    # If the host does not exist we need to create it
    try:
        myhostgroups = data['hostgroups']
    except:
        myhostgroups = []
    hostgroupids = []
    for hostgroup in myhostgroups:
        hostgroupinfo = get_hostgroup_id(hostname, token, hostgroup)
        groupid = hostgroupinfo['groupid']
        hostgroupids[hostgroup].append(groupid)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {token}"
    }
    method = 'host.create'
    params = {
        'host': data['hostname'],
        'groups': [
            {
                'groupid': hostgroupids
            }
        ],
        'templates': [
        ]
    }

    response = call_jsonrpc_api(hostname, headers, method, params)
    try:
        response = call_jsonrpc_api(hostname, headers, method, params)
    except requests.exceptions.RequestException as e:
        failed=True
        module.fail_json(msg=f"Failed to call Zabbix API: response: {params}   )  ")





def link_template(module, hostname, token, data):
    failed = False
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {token}"
    }
   # first we need the templateid of the template we want to link to
    method = 'template.get'
    templatetoaddname = data['template']
    params = {
        'output': 'extend',
        'filter': {
            'name': templatetoaddname
        }
    }
    try:
        response = call_jsonrpc_api(hostname, headers, method, params)
    except requests.exceptions.RequestException as e:
        failed=True
    myidtoadd = {"templateid": response['result'][0]['templateid']}
    # now we need to get the templateids linked to the systemrole template

    method = 'template.get'
    systemroletemplatename = data['systemrole']

    params = {
        'output': 'extend',
        'selectParentTemplates': 'extend',
        'filter': {
            'name': systemroletemplatename
        }
        
        }
    
    headers = {
        'Content-Type': 'application/json-rpc',
        'Authorization': f"Bearer {token}"
    }

    try:
        response = call_jsonrpc_api(hostname, headers, method, params)
    except requests.exceptions.RequestException as e:
        failed=True
    mycurrentids = []
    for item in response['result']:
        for parent in item['parentTemplates']:
            myid = {"templateid": parent['templateid']}
            if myid == myidtoadd:
                module.exit_json(changed=False, result="Template already linked")
            mycurrentids.append(myid)
    mycurrentids.append(myidtoadd)

    method = 'template.get'
    systemroletemplatename = data['systemrole']
    params = {
        'output': 'extend',
        'filter': {
            'name': systemroletemplatename
        }
    }
    try:
        response = call_jsonrpc_api(hostname, headers, method, params)
    except requests.exceptions.RequestException as e:
        failed=True
            
    systemroletemplateid = response['result'][0]['templateid']
    # now we need to link the template to the dashdb template   
    method = 'template.update'
    # templates: [ { templateid: "{{ zabbix_templateid_to_add }}" } ]
    testarray = []
    for item in mycurrentids:
        testarray.append(item)
    params = {
        'templateid': systemroletemplateid,
        'templates': testarray
    }

    try:
        response = call_jsonrpc_api(hostname, headers, method, params)
        module.exit_json(changed=True, result="Template linked")

    except requests.exceptions.RequestException as e:
        failed=True
        module.exit_json(changed=True, result="Template linked successfully")

    method = 'template.get'
    systemroletemplatename = data['systemrole']

    params = {
        'output': 'extend',
        'selectParentTemplates': 'extend',
        'filter': {
            'name': systemroletemplatename
        }
        
        }
    
    headers = {
        'Content-Type': 'application/json-rpc',
        'Authorization': f"Bearer {token}"
    }

    try:
        response = call_jsonrpc_api(hostname, headers, method, params)
    except requests.exceptions.RequestException as e:
        failed=True
    mycurrentids = []
    for item in response['result']:
        for parent in item['parentTemplates']:
            myid = {"templateid": parent['templateid']}
            if myid == myidtoadd:
                module.exit_json(changed=True, result="Template linked") 


def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(required=True, type='str'),
            token=dict(required=True, type='str', no_log=True),
            task=dict(required=True, type='str'),
            params=dict(required=True, type='dict'),
            state=dict(default='present', choices=['present', 'absent']),
        ),
        supports_check_mode=True,
    )

    hostname = module.params['hostname']
    token = module.params['token']
    task = module.params['task']
    params = module.params['params']

    check_mode = module.check_mode
    changed = False

    non_change_tasks = (
        'get_',
    )

    if not task.startswith(non_change_tasks):
        changed = True
        if check_mode:
            module.exit_json(changed=changed,result='')

    known_tasks = (
        'link_template',
        'get_host',
        'create_host',
    )

    if task not in known_tasks:
        module.fail_json(msg=f"Failed to call unknown task: {task}")

            
    if task == 'link_template':
        result = link_template(module, hostname, token, params)

    if task == 'get_host': 
        result = zabbix_host_get(module, hostname, token, params)
        module.exit_json(changed=False, result={result})

    if task == 'create_host':
        result = zabbix_host_create(module, hostname, token, params)
        module.exit_json(changed=True, result=result)

    module.fail_json(msg=f"Failed to call unknown task: {task}")
    print("This is the end of the function")

    return True

if __name__ == '__main__':
    main()
