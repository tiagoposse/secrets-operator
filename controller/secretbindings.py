import kopf
import kubernetes
import logging

from os import environ

if environ.get('USE_VAULT') in [ 'true', 'True', 'TRUE' ]:
  from backends.vault.api import process_vault_secret, grant_vault_access, revoke_vault_access

if environ.get('USE_AWS') in [ 'true', 'True', 'TRUE' ]:
  from backends.aws.api import grant_aws_access, revoke_aws_access

if environ.get('USE_GCP') in [ 'true', 'True', 'TRUE' ]:
  from backends.gcp.api import grant_gcp_access, revoke_gcp_access

logger = logging.getLogger()

@kopf.on.create('secretbindings.kscp.io')
def create_secret_binding(name, namespace, spec, **_):
  '''
    Process the creation of a secretbindings resource
  '''

  policies = {
    "vault": [],
    "aws": [],
    "gcp": []
  }

  for s in spec.get('secrets'):
    try:
      secret = read_secret_spec(s['name'], namespace, s['backend'])
    except kubernetes.client.exceptions.ApiException:
      raise kopf.PermanentError(f"Secret { s.get('name') } in { s.get('backend') } does not exist, please create first.")

    if s['backend'] == 'vault':
      policies['vault'].append(f"{ namespace }-{ s['name'] }")
    elif secret.get('spec').get('backend') == 'aws':
      policies['aws'].append(f"{ namespace }-{ s['name'] }")
    elif secret.get('spec').get('backend') == 'gcp':
      policies['gcp'].append(f"{ namespace }-{ s['name'] }")

  if len(policies['vault']) > 0:
    grant_vault_access(f"{ namespace }-{ spec.get('serviceAccount') }-{ name }", spec.get('serviceAccount'), namespace, policies['vault'])

  if len(policies['aws']) > 0:
    grant_aws_access(spec.get('serviceAccount'), s['name'], namespace)

  if len(policies['gcp']) > 0:
    grant_gcp_access(spec.get('serviceAccount'), s['name'], namespace)


@kopf.on.delete('secretbindings.kscp.io')
def delete_secret_binding(name, namespace, spec, **_):
  '''
    Process the deletion of a secretbindings resource
  '''

  binding_name = f"{ namespace }-{ spec.get('serviceAccount') }-{ name }"

  __revoke_vault = False
  __revoke_aws = False
  __revoke_gcp = False
  for s in spec.get('secrets'):
    if s.get('backend') == 'vault':
      __revoke_vault = True
    elif s.get('backend') == 'aws':
      __revoke_aws = True
    elif s.get('backend') == 'gcp':
      __revoke_gcp = True

  if __revoke_vault:
    revoke_vault_access(binding_name)
  
  if __revoke_aws:
    revoke_aws_access(binding_name)

  if __revoke_gcp:
    revoke_gcp_access(binding_name)


@kopf.on.update('secretbindings.kscp.io', field="spec")
def update_secret_binding(name, new, old, **_):
  '''
    Process the update of a secretbindings resource
  '''
  namespace = old.get('spec')
  old_binding_name = f"{ namespace }-{ old.get('spec').get('serviceAccount') }-{ name }"
  new_binding_name = f"{ namespace }-{ new.get('spec').get('serviceAccount') }-{ name }"
  __trigger_move = old_binding_name != new_binding_name

  names = []
  vault_policies = []

  for s in new.get('spec').get('secrets'):
    if s.get('backend') == 'vault':
      vault_policies.append(f"{ namespace }-{ s.get('name') }")
    elif s.get('backend') == 'aws':
      grant_aws_access(new.get('spec').get('serviceAccount'), s.get('name'), namespace)
      names.append(f"aws-{ s.get('name') }")
    elif s.get('backend') == 'gcp':
      grant_gcp_access(new.get('spec').get('serviceAccount'), s.get('name'), namespace)
      names.append(f"gcp-{ s.get('name') }")

  if len(vault_policies) > 0:
    grant_vault_access(new_binding_name, new.get('spec').get('serviceAccount'), s.get('name'), namespace, vault_policies)

  if __trigger_move:
    revoke_vault_access(old_binding_name)

  for s in old.get('spec').get('secrets'):
    if s.get('backend') == 'aws' and (f"aws-{ s.get('name') }" not in names or __trigger_move):
      revoke_aws_access(old.get('spec').get('serviceAccount'), s.get('name'), namespace)
    elif s.get('backend') == 'gcp' and (f"gcp-{ s.get('name') }" not in names or __trigger_move):
      revoke_gcp_access(old.get('spec').get('serviceAccount'), s.get('name'), namespace)


def read_secret_spec(name, namespace, backend):
  kubernetes.config.load_incluster_config()

  with kubernetes.client.ApiClient() as api_client:
    api_instance = kubernetes.client.CustomObjectsApi(api_client)
    api_response = api_instance.get_namespaced_custom_object(
      'kscp.io',
      'v1alpha1',
      namespace,
      f"{ backend }secrets",
      name
    )

  if api_response.get('backend') == 'vault':
    api_response = process_vault_secret(name, namespace, api_response)

  return api_response