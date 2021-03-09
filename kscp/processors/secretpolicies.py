import kubernetes

from controller.utils import get_change_path, generate_secret_values
from controller.controller import KSCPController

class PoliciesController:
  def __init__(self, controller: KSCPController):
    self.__controller = controller

  def get_policy_spec(self, name: str, namespace: str):
    '''
      Get the CRD resource from kubernetes
    '''

    api_instance = kubernetes.client.CustomObjectsApi(self.__controller.get_backend_client('k8s'))
    return api_instance.api_instance.get_namespaced_custom_object(
      'kscp.io',
      'v1alpha1',
      namespace,
      f"secretpolicies",
      name
    )

  def list_policy_specs(self, name: str, namespace: str):
    api_instance = kubernetes.client.CustomObjectsApi(self.__controller.get_backend_client('k8s'))
    return api_instance.api_instance.list_namespaced_custom_object(
      'kscp.io',
      'v1alpha1',
      namespace,
      f"secretpolicies",
      name
    )