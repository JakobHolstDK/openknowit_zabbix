#!/usr/bin/python

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

def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(required=True, type='str'),
            token=dict(required=True, type='str', no_log=True),
            method=dict(required=True, type='str'),
            params=dict(required=True, type='dict'),
        ),
        supports_check_mode=True,
    )

    hostname = module.params['hostname']
    token = module.params['token']
    method = module.params['method']
    params = module.params['params']
    check_mode = module.check_mode
    changed = False

    headers = {
        'Content-Type': 'application/json-rpc',
        'Authorization': f"Bearer {token}"
    }
    non_change_actions = (
        '.get',
        '.export',
        '.version',
        '.checkAuthentication',
        '.login',
        '.logout',
        '.getscriptsbyevents',
        '.getscriptsbyhosts'
    )

    if not method.endswith(non_change_actions):
        changed = True
        if check_mode:
            module.exit_json(changed=changed,result='')

    # Make the API call
    try:
        response = call_jsonrpc_api(hostname, headers, method, params)
    except requests.exceptions.RequestException as e:
        module.fail_json(msg=f"Failed to call Zabbix API: {e}")

    if 'error' in response:
        error = response['error']
        module.fail_json(msg=f"Zabbix API call failed: {error['message']}",
                         error_code=error['code'],
                         error_data=error.get('data'))


    module.exit_json(changed=changed, result=response.get('result'))


if __name__ == '__main__':
    main()
