import kubernetes
import logging

from controller.engine import KSCPEngine
from controller.exceptions import KSCPException
from controller.models.externalsecrets import ExternalSecret

logger = logging.getLogger()

class ExternalSecretsController:
  def __init__(self, controller: KSCPEngine):
    self.__controller = controller


  def get_secret(self, spec: dict):
    '''
      Return the secret values from the backend
    '''
    return self.__controller.get_backend_client(spec.get('backend')).get_secret(spec)


  def get_secret_spec(self, name: str, namespace: str):
    '''
      Get the CRD resource from kubernetes
    '''

    api_instance = kubernetes.client.CustomObjectsApi(self.__controller.get_backend_client('k8s'))

    try:
      return api_instance.api_instance.get_namespaced_custom_object(
        'kscp.io',
        'v1alpha1',
        namespace,
        f"externalsecrets",
        name
      )
    except kubernetes.client.exceptions.ApiException:
      raise KSCPException(404, f"Secret { namespace }/{ name } could not be found")


  def get_object_for_backend(self, name, namespace, backend, path = None, values = {}, config = {}):
    return self.__controller.get_backend_client(backend).get_object(name, namespace, path, values, config)


  def create_secret(self, secret: ExternalSecret) -> ExternalSecret:
    '''
      Process the creation of an externalsecrets resource
    '''

    backend_client = self.__controller.get_backend_client(secret.get_backend())
    secret.check_can_create()

    self.__controller.can_access_secret(secret)

    # changed_spec['values'], masked_values = generate_secret_values(values)
    backend_client.create_secret(secret)

    return secret


  def delete_secret(self, secret: ExternalSecret):
    '''
      Process the deletion of an externalsecrets resource
    '''

    self.__controller.can_access_secret(secret)

    if not self.__controller.can_access_secret(secret):
      return False

    self.__controller.get_backend_client(secret.get_backend()).delete_secret(secret)


  def update_secret(self, old_secret: ExternalSecret, new_secret: ExternalSecret):
    '''
      Process the update of an externalsecrets resource
    '''

    backend_client = self.__controller.get_backend_client(old_secret.get_backend())
    
    # when creation happens, this handler will skip updating.
    if old_secret.get_path() is None:
      return True

    self.__controller.can_access_secret(old_secret)

    __trigger_value_change = False
    old_values = old_secret.get_raw_values()
    new_values = new_secret.get_raw_values()
    real_values = None

    for k, v in new_values.items():
      if old_values.get(k) == v:
        if real_values is None:
          real_values = backend_client.get_secret(old_secret)
          if real_values is None:
            raise KSCPException(500, f"Values retrieved for path { old_secret.get_path() } are None")
        
        new_values[k] = real_values[k]

    new_secret.set_real_values(new_values)
    backend_client.update_secret(__trigger_value_change, old_secret, new_secret)

    return new_secret
