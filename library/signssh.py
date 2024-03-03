import requests
import json
import os
import time
from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = '''
'''
EXAMPLES = '''
'''
RETURN = '''
'''


def signssh(sshkey, vault_addr, vault_token):
    headers = {
        'X-Vault-Token': vault_token,
        'Content-Type': 'application/json',
    }

    data = {
        'public_key': sshkey,
        'valid_principals': 'root',
    }

    response = requests.post(f'{vault_addr}/v1/ssh-client-signer/sign/my-role', headers=headers, data=json.dumps(data), verify=True)
    response.raise_for_status()
    return response.json()['data']['signed_key']



def create_ssh_key(filename):
    from Crypto.PublicKey import RSA
    key = RSA.generate(2048)
    keystring = key.exportKey('OpenSSH').decode('utf-8')
    os.system("/usr/bin/touch %s " % filename)  # Create the file if it does not exist
    text_file = open(filename, "w") 
    text_file.write(keystring)
    text_file.close()
    return  keystring


def main():
    module = AnsibleModule(
        argument_spec=dict(
            vault_addr=dict(required=True, type='str'),
            vault_token=dict(required=True, type='str', no_log=True),
            method=dict(required=True, type='str'),
            params=dict(required=True, type='dict'),
        ),
        supports_check_mode=True,
    )


    vault_addr = module.params['vault_addr']
    token = module.params['vault_token']
    method = module.params['method']
    params = module.params['params']
    check_mode = module.check_mode
    changed = False
    token = "hvs.13HJTof2PbvGyu3jvvESxV5C"
    vault_addr = "https://vault.openknowit.com"

    headers = {
        'Content-Type': 'application/json-rpc',
        'Authorization': f"Bearer {token}"
    }

    if method == "auto":
    if True:
        # The signing will be on a "fresh ip key generated and stored i ~/.ssh/disposeable and the signed key i ~/.ssh/disposeable.signed
        filename = "/tmp/disposeable"
        sshkey = create_ssh_key(filename)
        signed_key = signssh(sshkey, vault_addr, token)
        signedfilename = filename + ".signed"

        os.system("/usr/bin/touch %s " % signedfilename)  # Create the file if it does not exist
        file1 =  open(signedfilename, "w") 
        file1.write(signed_key)
        file1.close()

        changed = True
        module.exit_json(changed=changed, signed_key=signed_key)

    module.exit_json(changed=changed, result=response.get('result'))


if __name__ == '__main__':
    main()

    





