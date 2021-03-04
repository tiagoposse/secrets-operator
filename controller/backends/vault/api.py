import logging
import kopf

# from backends.vault.policies import VaultPolicy
# from backends.vault.roles import VaultRole
from backends.vault.client import get_vault_client
from utils import generate_secret_values, get_change_path

from os import environ

logger = logging.getLogger()

__client = get_vault_client()


@kopf.on.create('vaultsecrets.kscp.io')
def create_secret(name, namespace, spec, **_):
  '''
    Process the creation of a vaultsecrets resource
  '''

  path = get_vault_resource_path(name, namespace, spec)
  mount_point = spec.get('mountPoint')

  values = spec.get('values')
  if not values:
    raise kopf.PermanentError(f"Values must be set. Got { values }.")

  __client.secrets.kv.v2.create_or_update_secret(
    path,
    secret=generate_secret_values(values),
    mount_point=mount_point
  )

  policy_name = f"{ namespace }-{ name }"

  logger.debug(f"Creating policy {policy_name}")
  __client.sys.create_or_update_policy(policy_name, f"path \"{ mount_point }/{ path }\" {{\n  capabilities = [\"read\"]\n}}\n")



@kopf.on.delete('vaultsecrets.kscp.io')
def delete_secret(name, namespace, spec, **_):
  '''
    Process the deletion of a vaultsecrets resource
  '''
  path = get_vault_resource_path(name, namespace, spec)

  __client.secrets.kv.v2.delete_metadata_and_all_versions(
    path,
    mount_point=spec.get('mountPoint')
  )

  logger.debug(f"Deleted secret { spec.get('mountPoint') }/{ path } in vault.")
  
  policy_name = f"{ namespace }-{ name }"

  __client.sys.delete_policy(policy_name)
  logger.debug(f"Deleted policy {policy_name}")


@kopf.on.update('vaultsecrets.kscp.io')
def update_secret(name, namespace, old, new, diff, **_):
  '''
    Process the update of a vaultsecrets resource
  '''
  
  new_spec = new.get('spec').copy()
  __trigger_value_change = False
  __trigger_move = False

  values = get_vault_secret(name, namespace, old.get('spec'))

  for op, path, old_val, new_val in diff:
    change_path = get_change_path(path)
    
    if change_path in [ '.spec.path', '.spec.mountPoint' ]:
      __trigger_move = True
      continue
    elif change_path.startswith('.spec.values.'):
      __trigger_value_change = True

      if op == 'delete':
        del values[path[-1]]
      else:
        values[path[-1]] = new_val

  if __trigger_move:
    delete_secret(name, namespace, old)
    
  if __trigger_value_change or __trigger_move:
    new_spec['values'] = generate_secret_values(values)
    # logger.debug(new_spec['spec']['values'])
    create_secret(name, namespace, new_spec)

  return True

def get_vault_resource_path(name, namespace, spec):
  if spec.get('path') is not None:
    return spec.get('path')

  return f"{ namespace }/{ name }"
    

def process_vault_secret(name, namespace, spec):
  if spec.get('path') is None:
    spec.set('path', f"{ namespace }/{ name }")

  return spec


def get_vault_secret(name, namespace, spec):
  path = get_vault_resource_path(name, namespace, spec)

  values = __client.secrets.kv.v2.read_secret_version(
    path,
    mount_point=spec.get('mountPoint')
  )["data"]["data"]

  logger.debug(f"Found secret { path } in vault.")
  return values


def grant_vault_access(uri, s_account, namespace, policies):
  __client.auth.kubernetes.create_role(
    uri,
    [s_account],
    [namespace],
    policies=policies
  )


def revoke_vault_access(uri):
  __client.auth.kubernetes.delete_role(uri)



# @classmethod
# def list(self, orig_path):
#   path, mount_point = self.get_mount_point_and_path(orig_path)

#   secret_names = client.secrets.kv.v2.list_secrets(path, mount_point=mount_point)
#   secrets = []
#   for sec in secret_names:
#     ret = self.get(sec)
#     if not ret:
#       raise Exception(f"Erro retrieving { sec } from vault.")
    
#     secrets.append(sec)

#   return secrets

# @staticmethod
# def get_mount_point_and_path(path: str) -> Tuple[str, str]:
#     """
#     Given a vault path, split it into path and mount_point
#     :rtype: str Path
#     :rtype: str Mount point
#     """
#     splitted = path.split("/")

#     return "/".join(splitted[1:]), splitted[0]


# ##############
# ### ROLES ###
# ##############

# @kopf.on.create('vaultroles.kscp.io')
# def create_vault_role(spec, name, **kwargs):
#     VaultRole(
#       name,
#       spec.get('boundServiceAccounts'),
#       spec.get('boundNamespaces'),
#       spec.get('policies')
#     ).create(get_vault_client())

# @kopf.on.delete('vaultroles.kscp.io')
# def delete_vault_role(name, **kwargs):
#   VaultRole(
#     name,
#     None,
#     None,
#     None
#   ).delete(get_vault_client())

# @kopf.on.update('vaultroles.kscp.io')
# def update_vault_role(name, new, **kwargs):
#     create_vault_role(new['spec'], name)


# ##############
# ## POLICIES ##
# ##############

# @kopf.on.create('vaultpolicies.kscp.io')
# def create_vault_policy(spec, name, **kwargs):
#     rules = spec.get('rules')

#     if not rules:
#         raise kopf.PermanentError(f"Rules must be set. Got {rules!r}.")

#     for r in rules:
#       if 'path' not in r:
#           raise kopf.PermanentError(f"Path not set for rule {r!r}.")

#     VaultPolicy(name, rules).create(get_vault_client())

# @kopf.on.delete('vaultpolicies.kscp.io')
# def delete_vault_policy(name, **kwargs):
#   VaultPolicy.delete(get_vault_client(), name)

# @kopf.on.update('vaultpolicies.kscp.io')
# def update_vault_policy(name, new, **kwargs):
#     create_vault_policy(new['spec'], name, **kwargs)