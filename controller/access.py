import kubernetes
import logging

logger = logging.getLogger()


class AccessEngine:
  def __init__(self, clients, is_auth_backend):
    self.__clients = clients
    self.__is_backend_auth = is_auth_backend

  def grant_access(self, name, namespace, spec):
    if self.__is_backend_auth:
      fn = self.__grant_access_in_backend
    else:
      fn = self.__grant_access_in_k8s
    
    fn(name, namespace, spec)

  def revoke_access(self, name, namespace, spec):
    if self.__is_backend_auth:
      fn = self.__revoke_access_in_backend
    else:
      fn = self.__revoke_access_in_k8s
    
    fn(name, namespace, spec)



  def __grant_access_in_backend(self, name, namespace, spec):
    policies = {}
    for backend in self.__backends:
      policies[backend] = []

    for s in spec.get('secrets'):
      try:
        secret = self.get_secret_spec(s['name'], namespace)
      except kubernetes.client.exceptions.ApiException:
        raise Exception(f"Secret { namespace }/{ name } could not be found")

      policies[secret.get('spec').get('backend')].append(f"{ namespace }-{ s['name'] }")

    for backend, policies in policies.items():
      if len(policies) == 0:
        continue

    return self.__clients.get(spec.get('backend')).revoke_access(
      spec.get('serviceAccount'),
      name,
      namespace,
      policies
    )

  def __grant_access_in_k8s(self, name, namespace, spec):
    resource_name = f"kscp-{ name }"
    role = kubernetes.client.V1Role(
      metadata = kubernetes.client.V1ObjectMeta(
        name = resource_name,
        namespace = namespace
      ),
      rules = [
        kubernetes.client.V1PolicyRule(
          api_groups = ['kscp.io'],
          resources = ['externalsecrets'],
          resource_names = [ s['name'] for s in spec.get('secrets') ],
          verbs = ['get']
        ),
        kubernetes.client.V1PolicyRule(
          api_groups = ['kscp.io'],
          resources = ['secretbindings'],
          resource_names = [name],
          verbs = ['get']
        )
      ]
    )

    role_binding = kubernetes.client.V1RoleBinding(
      role_ref = kubernetes.client.V1RoleRef(
        api_group = 'rbac.authorization.k8s.io',
        kind = 'Role',
        name = resource_name,
      ),
      metadata = kubernetes.client.V1ObjectMeta(
        name = resource_name,
        namespace = namespace
      ),
      subjects = [
        kubernetes.client.V1Subject(
          kind = 'ServiceAccount',
          name = spec.get('serviceAccount'),
          namespace = namespace
        )
      ]
    )

    api_instance = kubernetes.client.RbacAuthorizationV1Api(self.__clients.get('k8s'))
    try:
      api_instance.create_namespaced_role(namespace, role)
    except kubernetes.client.exceptions.ApiException as e:
      if e.status != 409:
        raise e

    try:
      api_instance.create_namespaced_role_binding(namespace, role_binding)
    except kubernetes.client.exceptions.ApiException as e:
      if e.status != 409:
        raise e


  def __revoke_access_in_k8s(self, name, namespace, spec):
    api_instance = kubernetes.client.RbacAuthorizationV1Api(self.__clients.get('k8s'))
    try:
      api_instance.delete_namespaced_role(f"kscp-{ name }", namespace)
    except kubernetes.client.ApiException as e:
      if e.status != 404:
        raise e
      else:
        logger.debug(f"Role kscp-{ name } did not exist, skip.")

    try:
      api_instance.delete_namespaced_role_binding(f"kscp-{ name }", namespace)
    except kubernetes.client.ApiException as e:
      if e.status != 404:
        raise e
      else:
        logger.debug(f"Role binding kscp-{ name } did not exist, skip.")


  def __revoke_access_in_backend(self, name, namespace, spec):
    revoke_backends = {}
    for backend in self.__backends:
      revoke_backends[backend] = False

    for s in spec.get('secrets'):
      try:
        secret = self.get_secret_spec(s['name'], namespace)
      except kubernetes.client.exceptions.ApiException:
        raise Exception(f"Secret { namespace }/{ name } could not be found")

      revoke_backends[secret.get('spec').get('backend')] = True

    for backend, should_revoke in revoke_backends.items():
      if should_revoke:
        self.__clients.get(backend).revoke_access(spec.get('serviceAccount'), name, namespace,)