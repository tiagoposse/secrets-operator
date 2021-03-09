import kubernetes

from controller.utils import get_change_path, generate_secret_values
from controller.controller import KSCPController

class SecretsController:
  def __init__(self, controller: KSCPController):
    self.__controller = controller


  def get_secret(self, spec: dict):
    '''
      Return the secret values from the backend
    '''
    return self.__controller.get_backend_client(spec.get('backend')).get_secret(spec)


  def get_secret_spec(self,  name: str, namespace: str):
    '''
      Get the CRD resource from kubernetes
    '''

    api_instance = kubernetes.client.CustomObjectsApi(self.__controller.get_backend_client('k8s'))
    return api_instance.api_instance.get_namespaced_custom_object(
      'kscp.io',
      'v1alpha1',
      namespace,
      f"externalsecrets",
      name
    )


  def create_secret(self, name: str, namespace: str, spec: dict):
    '''
      Process the creation of an externalsecrets resource
    '''

    values = spec.get('values')
    if not values:
      raise Exception(f"Values must be set. Got { values }.")

    new_spec = spec.copy()
    new_spec['values'] = generate_secret_values(values)

    return self.__controller.get_backend_client(spec.get('backend')).create_secret(name, namespace, new_spec)


  def delete_secret(self,  name: str, namespace: str, spec: dict):
    '''
      Process the deletion of an externalsecrets resource
    '''

    self.__controller.get_backend_client(spec.get('backend')).delete_secret(name, namespace, spec)


  def update_secret(self, name: str, namespace: str, old: dict, new: dict, diff: dict):
    '''
      Process the update of an externalsecrets resource
    '''

    backend_client = self.__controller.get_backend_client(old.get('backend'))

    __trigger_move = new.get('spec').get('path') != old.get('spec').get('path')
    __trigger_value_change = False
    values = backend_client.get_secret(old.get('spec'))

    for op, path, old_val, new_val in diff:
      change_path = get_change_path(path)

      if not change_path.startswith('.spec.values.'):
        continue

      __trigger_value_change = False

      if op == 'delete':
        del values[path[-1]]
      else:
        values[path[-1]] = new_val

    new_spec = new['spec'].copy()
    new_spec['values'] = generate_secret_values(values)

    backend_client.update_secret(name, namespace, __trigger_move, __trigger_value_change, new_spec)