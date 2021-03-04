import boto3
import json
import kopf

from os import environ

from utils import generate_secret_values, get_change_path

if environ.get('USE_AWS') in [ 'true', 'True', 'TRUE' ]:
  __client = boto3.client('secretsmanager')
  __aws_account_id = environ.get('aws_account_id')

aws_policy_template = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "system:serviceaccount:"
      },
      "Action": "secretsmanager:GetSecretValue",
      "Resource":"*"
    }
  ]
}


@kopf.on.create('awssecrets.kscp.io')
def create_secret(name, namespace, spec, **kwargs):
  '''
    Process the creation of an awssecrets resource
  '''

  response = __client.create_secret(
    Name=name,
    ClientRequestToken='string',
    SecretBinary=generate_secret_values(spec.get('values')).encode('utf-8')
  )


@kopf.on.delete('awssecrets.kscp.io')
def delete_secret(name, namespace, spec, **kwargs):
  '''
    Process the deletion of an awssecrets resource
  '''

  response = __client.delete_secret(
    RecoveryWindowInDays=7,
    SecretId=name,
  )


@kopf.on.update('awssecrets.kscp.io')
def update_secret(name, namespace, old, new, diff, **kwargs):
  '''
    Process the update of an awssecrets resource
  '''

  values = read_aws_secret(name)

  for op, path, old_val, new_val in diff:
    change_path = get_change_path(path)

    if not change_path.startswith('.spec.values.'):
      continue

    if op == 'delete':
      del values[path[-1]]
    else:
      values[path[-1]] = new_val

  __client.put_secret_value(
    SecretId=f"{ namespace }-{ name }",
    SecretBinary=generate_secret_values(values).encode('utf-8')
  )


def read_aws_secret(name):
  return __client.get_secret_value(
    SecretId=name
  ).SecretBinary.decode('utf-8')


def grant_aws_access(s_account, name):
  pol = aws_policy_template.copy()
  pol['Statement']['Principal']['AWS'] += f"{ __aws_account_id }:{ s_account }"
  
  __client.put_resource_policy(
    SecretId=name,
    ResourcePolicy=json.dumps(pol),
    BlockPublicPolicy=True|False
  )

def revoke_aws_access(s_account, name):
  pass
  # pol = aws_policy_template.copy()
  # pol['Statement']['Principal']['AWS'] += f"{ __aws_account_id }:{ s_account }"

  # __client.put_resource_policy(
  #   SecretId=name,
  #   ResourcePolicy=json.dumps(pol),
  #   BlockPublicPolicy=True|False
  # )