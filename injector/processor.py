import json
import kubernetes

from flask import current_app
from os import environ

class KSCPProcessor:
  def __init__(self, vault, aws, gcp):
    self.__vault_client = vault
    self.__aws_client = aws
    self.__gcp_client = gcp

    if environ.get('K8S_CA_CERT'):
      self.k8s_ca_cert = environ.get('K8S_CA_CERT')
    else:
      self.k8s_ca_cert = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"


  def get_k8s_conf_for_request(self, auth):
      conf = kubernetes.client.Configuration()
      kubernetes.config.load_incluster_config(client_configuration=conf)
      conf.api_key['authorization'] = auth
      conf.api_key_prefix['authorization'] = 'Bearer'
      conf.ssl_ca_cert = self.k8s_ca_cert

      return conf

  def process_secret_read(self, auth, name, namespace):
      if name.count('/') > 1:
        secret_types = [name.split('/')[0]]
        name = '/'.join(name.split('/')[1:])
      else:
        secret_types = ['aws', 'gcp', 'vault']

      responses = {}
      with kubernetes.client.ApiClient(self.get_k8s_conf_for_request(auth)) as api_client:
        api_instance = kubernetes.client.CustomObjectsApi(api_client)

        for sec_type in secret_types:
          try:
            responses[sec_type] = api_instance.get_namespaced_custom_object(
              'kscp.io',
              'v1alpha1',
              namespace,
              f"{ sec_type }secrets",
              name
            )

            current_app.logger.debug(responses[sec_type])
          except kubernetes.client.exceptions.ApiException as e:
            if e.status == 404:
              pass
            else:
              raise e

      response_keys = list(responses.keys())
      current_app.logger.debug(response_keys)

      if len(responses) > 1:
        return json.dumps({ "error": f"Found secret { name } in { ', '.join(responses.keys()) }. Please provide secret name like { response_keys[0] }/{ name }" }), 500
      elif len(responses) == 0:
        return json.dumps({ "error": f"Secret { name } not found in { response_keys[0] }/{ name }" }), 500
      
      api_response = list(responses.values())[0]
      backend = list(responses.keys())[0]
      
      # READ SECRET VALUES
      if backend == 'vault':
        values = self.__vault_client.secrets.kv.v2.read_secret_version(
            api_response['spec']['path'], mount_point=api_response['spec']['mountPoint']
        )["data"]["data"]
      elif backend == 'aws':
        values = self.__aws_client.get_secret_value(
          SecretId=name
        ).SecretBinary.decode('utf-8')
      elif backend == 'gcp':
        values = self.__gcp_client.access_secret_version(
          name=f"projects/{environ.get('PROJECT_ID')}/secrets/{name}/versions/latest"
        ).payload.data.decode('UTF-8')

      current_app.logger.info(values)
      return values