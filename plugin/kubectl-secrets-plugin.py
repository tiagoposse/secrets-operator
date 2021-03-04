import sys
import kubernetes
from kubernetes import config
import base64

target = {
  "service": "kscp-injector"
}

def get_args(line):
  namespace = None
  name = None

  i = 0
  while i < len(line):
    if line[i] in [ '-n', '--namespace' ]:
      namespace = line[i+1]
      i += 1
    else:
      name = line[i]

    i += 1

  return name, namespace

def main():
    conf = kubernetes.client.Configuration()
    config.load_kube_config(client_configuration=conf)

    client = kubernetes.client.ApiClient(conf)

    name, namespace = get_args(sys.argv[1:])

    body = {
        "auth": base64.b64decode(client.configuration.api_key.get('authorization').split(" ")[1].encode('utf-8')).decode('utf-8'),
        "secret": name,
        "backend": "vault",
        "namespace": namespace
    }

    response = client.call_api(
      "/api/v1/namespaces/secretsplane/services/https:{service}:443/proxy/readsecret", 'POST',
      { "service": target['service'] },
      [],
      {"Accept": "application/json"},
      body=body,
      post_params=[],
      files={},
      response_type='object',  
      auth_settings=["BearerToken"],
      async_req=False,
      _return_http_data_only=True, 
      _preload_content=True,
      _request_timeout=None,
      collection_formats={}
    )

    for k, v in response['data'].items():
      print(f"{ k } = { v }")

if __name__ == "__main__":
  main()