import kubernetes

class SecretsController:
  def __init__(self, controller):
    self.__controller = controller


  def get_secret(self, spec):
    return self.__controller.get_backend_client(spec.get('backend')).get_secret(spec)


  def get_secret_spec(self, name, namespace):
    api_instance = kubernetes.client.CustomObjectsApi(self.__controller.get_backend_client('k8s'))
    return api_instance.api_instance.get_namespaced_custom_object(
      'kscp.io',
      'v1alpha1',
      namespace,
      f"externalsecrets",
      name
    )


  def create_secret(self, name, namespace, spec):
    '''
      Process the creation of an externalsecrets resource
    '''

    values = spec.get('values')
    if not values:
      raise Exception(f"Values must be set. Got { values }.")

    return self.__controller.get_backend_client(spec.get('backend')).create_secret(name, namespace, spec)


  def delete_secret(self, name, namespace, spec):
    '''
      Process the deletion of an externalsecrets resource
    '''

    self.__controller.get_backend_client(spec.get('backend')).delete_secret(name, namespace, spec)


  def update_secret(self, name, namespace, old, new, diff):
    '''
      Process the update of an externalsecrets resource
    '''
    
    self.__controller.get_backend_client(old.get('backend')).update_secret(name, namespace, old, new, diff)