import boto3
import hvac
import json
import logging
import re

from google.cloud import secretmanager
from os import environ

logging.info("starting")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__vault_client = None
__gcp_client = None
__aws_client = None

def get_vault_client(role):
  with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as f:
    token = f.read()

  client = hvac.Client(url=environ.get('VAULT_ADDR'))
  client.auth.kubernetes.login(
    role,
    token,
    use_token=True
  )
  return client

def get_aws_client():
  return boto3.client('secretsmanager')

def get_gcp_client():
  return secretmanager.SecretManagerServiceClient()


if environ.get('USE_AWS') and environ.get('AWS_ACCOUNT_ID') and environ.get('AWS_REGION'):
  __aws_client = get_aws_client()

if environ.get('USE_GCP') and environ.get('GCP_PROJECT_ID'):
  __gcp_client = get_gcp_client()
  

def read_aws_secret(name):
  return json.loads(
    __aws_client.get_secret_value(
      SecretId=name
    ).SecretBinary.decode('utf-8')
  )

def read_gcp_secret(name, version = "latest"):
  return json.loads(
    __gcp_client.access_secret_version(
      name=f"projects/{ environ.get('GCP_PROJECT_ID')} /secrets/{name}/versions/{version}"
    ).payload.data.decode('UTF-8')
  )

def read_vault_secret(vault_client, path):
  split_path = path.split('/')
  return vault_client.secrets.kv.v2.read_secret_version(
    '/'.join(split_path[1:]),
    mount_point=split_path[0]
  )["data"]["data"]

def get_secrets_for_bind(bind):
  secret_values = []
  if environ.get('USE_VAULT') in ['true', 'True']:
    __vault_client = get_vault_client(bind.get('vault_role'))

    for s in bind['vault_secrets']:
      logging.info(f"Retrieving vault secret { s }")
      secret_values.append(read_vault_secret(__vault_client, s))

  if environ.get('USE_AWS') in ['true', 'True']:
    for s in bind['aws_secrets']:
      logging.info(f"Retrieving aws secret { s }")
      secret_values.append(read_aws_secret(s))

  if environ.get('USE_GCP') in ['true', 'True']:
    for s in bind['gcp_secrets']:
      logging.info(f"Retrieving gcp secret { s }")
      secret_values.append(read_gcp_secret(s))
  
  return secret_values


def main():
  binds = []

  for k, v in environ.items():
    bind_match = re.match(r'^BIND_(.+)$', k)
    if bind_match:
      binds.append(json.loads(v))

  for b in binds:
    bind_secrets = get_secrets_for_bind(b)

    if b.get('template') is None:
      empty_template = True
      template = ""
    else:
      empty_template = False
      template = b.get('template')

    for s in bind_secrets:
      for k, v in s.items():
        if empty_template:
          template += f"{ k }={ v }\n"
        else:
          template.replace(f"{{{{ { s }.{ k } }}}}", v)

    with open(b.get('target'), 'w+') as f:
      f.write(template)

if __name__ == '__main__':
  main()