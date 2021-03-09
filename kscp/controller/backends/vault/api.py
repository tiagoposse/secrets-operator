import logging

from os import environ

from backends.vault.client import get_vault_client

logger = logging.getLogger()

def get_api_instance():
  return VaultBackend()

class VaultBackend:
  def __init__(self):
    self.__client = get_vault_client()
    self.__default_mount_point = environ.get('VAULT_DEFAULT_MOUNT_POINT')


  def create_secret(self, name, namespace, spec):
    '''
      Process the creation of a vaultsecrets resource
    '''

    mount_point, path = self.__get_mount_point_and_path(spec.get('path'), name, namespace)
    
    self.__client.secrets.kv.v2.create_or_update_secret(
      path,
      secret=spec.get('values'),
      mount_point=mount_point
    )
    logger.debug(f"Created secret { mount_point }/{ path } in vault.")

    # policy_name = f"{ namespace }-{ name }"

    # self.__client.sys.create_or_update_policy(policy_name, f"path \"{ mount_point }/{ path }\" {{\n  capabilities = [\"read\"]\n}}\n")
    # logger.debug(f"Created policy {policy_name}")

    return f"{ mount_point }/{ path }"


  def delete_secret(self, name, namespace, spec):
    '''
      Process the deletion of a vaultsecrets resource
    '''
  
    mount_point, path = self.__get_mount_point_and_path(spec.get('path'), name, namespace)

    self.__client.secrets.kv.v2.delete_metadata_and_all_versions(
      path,
      mount_point=mount_point
    )

    logger.debug(f"Deleted secret { mount_point }/{ path } in vault.")
    
    policy_name = f"{ namespace }-{ name }"

    # self.__client.sys.delete_policy(policy_name)
    # logger.debug(f"Deleted policy {policy_name}")


  def update_secret(self, name, namespace, __trigger_move, __trigger_value_change, old_spec, new_spec):
    '''
      Process the update of a vaultsecrets resource
    '''

    if __trigger_move:
      self.delete_secret(name, namespace, old_spec)
      
    elif __trigger_value_change or __trigger_move:
      self.create_secret(name, namespace, new_spec)

    return True
      

  def get_secret(self, spec):
    path = spec.get('path').split('/')

    values = self.__client.secrets.kv.v2.read_secret_version(
      '/'.join(path[1:]),
      mount_point=path[0]
    )["data"]["data"]

    logger.debug(f"Found secret { path } in vault.")
    return values


  def grant_access(self, s_account, name, namespace, policies):
    self.__client.auth.kubernetes.create_role(
      f"{ namespace }-{ s_account }-{ name }",
      [s_account],
      [namespace],
      policies=policies
    )


  def revoke_access(self, s_account, name, namespace):
    self.__client.auth.kubernetes.delete_role(f"{ namespace }-{ s_account }-{ name }")


  def __get_mount_point_and_path(self, path, name, namespace):
    if path is None:
      return self.__default_mount_point, f"{ namespace }/{ name }"

    split_path = path.split('/')
    if len(split_path) == 1:
      return self.__default_mount_point, f"{ path }/{ name }"
    
    return split_path[0], '/'.join(split_path[1:])