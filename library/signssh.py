import requests
import json
from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = '''
'''
EXAMPLES = '''
'''
RETURN = '''
'''


def signssh(sshkey, vault_addr, vault_token, vault_ca):
    headers = {
        'X-Vault-Token': vault_token,
        'Content-Type': 'application/json',
    }

    data = {
        'public_key': sshkey,
        'valid_principals': 'root',
    }

    response = requests.post(f'{vault_addr}/v1/ssh-client-signer/sign/client', headers=headers, data=json.dumps(data), verify=vault_ca)
    response.raise_for_status()
    return response.json()['data']['signed_key']



def create_ssh_key(filename):
    from Crypto.PublicKey import RSA
    key = RSA.generate(2048)
    keystring = key.exportKey('OpenSSH').decode('utf-8')
    # open file and overwrite if exists whith the keysting in filename
    f = open(filename, 'w')
    f.write(keystring)
    f.close()
    return  True


def main():
    module = AnsibleModule(
        argument_spec=dict(
            vault_addr=dict(required=True, type='str'),
            token=dict(required=True, type='str', no_log=True),
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

    headers = {
        'Content-Type': 'application/json-rpc',
        'Authorization': f"Bearer {token}"
    }

    if method == "auto":
        # The signing will be on a "fresh ip key generated and stored i ~/.ssh/disposeable and the signed key i ~/.ssh/disposeable.signed

        create_ssh_key("~/.ssh/disposeable")
        sshkey = open("~/.ssh/disposeable").read()
        signed_key = signssh(sshkey, vault_addr, token, "vault_ca")
        f = open("~/.ssh/disposeable.signed", "w")
        f.write(signed_key)
        f.close()
        changed = True
        module.exit_json(changed=changed, signed_key=signed_key)

    





