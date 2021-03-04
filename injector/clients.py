import boto3
import hvac

from flask import current_app
from google.cloud import secretmanager
from os import environ

def setup_clients(use_vault, use_gcp, use_aws):
  __vault_client = None
  __aws_client = None
  __gcp_client = None

  if use_vault:
    __vault_client = get_vault_client()

  if use_gcp:
    __gcp_client = secretmanager.SecretManagerServiceClient()

  if use_aws:
    __aws_client = boto3.client('secretsmanager')

  return __vault_client, __aws_client, __gcp_client

def get_vault_client():
    addr = environ.get('VAULT_ADDR')

    token = "/vault/secrets/token"
    if token is None:
        raise Exception(
            "Please specify a path to the vault token either via --token or $VAULT_TOKEN"
        )

    with open(token, "r") as f:
        token = f.read().rstrip()

    client = hvac.Client(url=addr, token=token)
    if client.is_authenticated():
        return client
    else:
        raise Exception("Authentication to vault unsuccessful")