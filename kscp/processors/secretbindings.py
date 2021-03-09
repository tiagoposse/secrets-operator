import kubernetes
import logging

from controller.controller import KSCPController

logger = logging.getLogger()

class SecretBindingsController:
  def __init__(self, controller: KSCPController):
    self.__controller = controller

  def get_secretbinding_spec(self, name: str, namespace: str):
    api_instance = kubernetes.client.CustomObjectsApi(self.__controller.get_backend_client('k8s'))
    return api_instance.get_namespaced_custom_object(
      'kscp.io',
      'v1alpha1',
      namespace,
      f"secretbindings",
      name
    )

  def update_secret_binding(self, name: str, namespace: str, new: dict, old: dict):
    '''
      Process the update of a secretbindings resource
    '''

    self.delete_secret_binding(name, namespace, old.get('spec'))
    self.create_secret_binding(name, namespace, new.get('spec'))


  def create_secret_binding(self, name: str, namespace: str, spec: dict):
    '''
      Process the creation of a secretbindings resource
    '''

    self.__controller.grant_access(name, namespace, spec)

  def delete_secret_binding(self, name: str, namespace: str, spec: dict):
    '''
      Process the deletion of a secretbindings resource
    '''

    self.__controller.revoke_access(name, namespace, spec)

  # def update_secret_binding(self, name, namespace, new, old):
  #   '''
  #     Process the update of a secretbindings resource
  #   '''
  #   old_binding_name = f"{ namespace }-{ old.get('spec').get('serviceAccount') }-{ old.get('name') }"
  #   new_binding_name = f"{ namespace }-{ new.get('spec').get('serviceAccount') }-{ new.get('name') }"
  #   __trigger_move = old_binding_name != new_binding_name

  #   revoke_backends = {}
  #   grant_policies = {}
  #   for backend in self.__backends:
  #     revoke_backends[backend] = False
  #     grant_policies[backend] = []

  #   for s in new.get('spec').get('secrets'):
  #     try:
  #       secret = self.get_secret_spec(s['name'], namespace)
  #     except kubernetes.client.exceptions.ApiException:
  #       raise Exception(f"Secret { namespace }/{ name } could not be found")

  #     grant_policies[secret.get('spec').get('backend')].append(f"{ namespace }-{ secret.get('name') }")

  #   if __trigger_move:
  #     for backend, should_revoke in revoke_backends.items():
  #       if should_revoke:
  #         self.__clients[backend].revoke_access(old_binding_name)

  #   for backend, policies in grant_policies.items():
  #     if len(policies) == 0:
  #       continue

  #     self.__clients.get(backend).grant_access(new.get('spec').get('serviceAccount'), old.get('name'), namespace, policies)
