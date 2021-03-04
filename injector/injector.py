import kubernetes

class KSCPInjector:
  def __init__(self, use_vault, use_aws, use_gcp):
    self.__use_vault = use_vault
    self.__use_aws = use_aws
    self.__use_gcp = use_gcp

    kubernetes.config.load_incluster_config()
    self.__k8s_client = kubernetes.client.CustomObjectsApi()

  def get_bind_conf(self, bind, namespace, vault_secrets, aws_secrets, gcp_secrets):
    bind_conf = {
      'template': bind.get('template'),
      'target': bind.get('target')
    }

    if self.__use_vault:
      bind_conf['vault_role'] = f"{ namespace }-{ bind.get('obj').get('spec').get('serviceAccount') }-{ bind.get('name') }"
      bind_conf['vault_secrets'] = vault_secrets

    if self.__use_aws:
      bind_conf['gcp_secrets'] = gcp_secrets
    
    if self.__use_gcp:
      bind_conf['aws_secrets'] = aws_secrets

    return bind_conf

  def get_vaultsecret_spec(self, name, namespace):
    return self.__k8s_client.get_namespaced_custom_object('kscp.io', 'v1alpha1', namespace, 'vaultsecrets', name)

  def get_secret_binding(self, name, namespace):
    return self.__k8s_client.get_namespaced_custom_object('kscp.io', 'v1alpha1', namespace, 'secretbindings', name)
