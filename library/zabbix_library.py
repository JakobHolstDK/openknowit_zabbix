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
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()


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
            
    if task == 'link_template':
        result = link_template(module, hostname, token, params)
    module.exit_json(changed=True, result="ok")

    print("This is the end of the function")
    return True

if __name__ == '__main__':
    main()
