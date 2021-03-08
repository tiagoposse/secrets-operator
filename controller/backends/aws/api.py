import boto3
import json

from os import environ

from utils import generate_secret_values, get_change_path

def get_api_instance():
  return AWSBackend()

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

class AWSBackend:
  def __init__(self):
    self.__client = boto3.client('secretsmanager')
    self.__aws_account_id = environ.get('aws_account_id')


  def create_secret(self, name, namespace, spec):
    '''
      Process the creation of an awssecrets resource
    '''

    path = f"{ namespace }/{ name }" if spec.get('path') is None else spec.get('path')

    self.__client.create_secret(
      Name=path,
      ClientRequestToken='string',
      SecretBinary=generate_secret_values(spec.get('values')).encode('utf-8')
    )

    return path

  def delete_secret(self, name, namespace, spec):
    '''
      Process the deletion of an awssecrets resource
    '''
    path = f"{ namespace }/{ name }" if spec.get('path') is None else spec.get('path')

    self.__client.delete_secret(
      RecoveryWindowInDays=7,
      SecretId=path,
    )


  def update_secret(self, name, namespace, old, new, diff):
    '''
      Process the update of an awssecrets resource
    '''

    values = self.read_secret(name)

    for op, path, old_val, new_val in diff:
      change_path = get_change_path(path)

      if not change_path.startswith('.spec.values.'):
        continue

      if op == 'delete':
        del values[path[-1]]
      else:
        values[path[-1]] = new_val

    self.__client.put_secret_value(
      SecretId=f"{ namespace }-{ name }",
      SecretBinary=generate_secret_values(values).encode('utf-8')
    )


  def get_secret(self, name, namespace, spec):
    path = f"{ namespace }/{ name }" if spec.get('path') is None else spec.get('path')

    return self.__client.get_secret_value(
      SecretId=path
    ).SecretBinary.decode('utf-8')


  def grant_access(self, s_account, name, namespace):
    pol = aws_policy_template.copy()
    pol['Statement']['Principal']['AWS'] += f"{ self.__aws_account_id }:{ s_account }"
    
    self.__client.put_resource_policy(
      SecretId=name,
      ResourcePolicy=json.dumps(pol),
      BlockPublicPolicy=True|False
    )

  def revoke_access(self, s_account, name, namespace):
    pass
    # pol = aws_policy_template.copy()
    # pol['Statement']['Principal']['AWS'] += f"{ __aws_account_id }:{ s_account }"

    # self.__client.put_resource_policy(
    #   SecretId=name,
    #   ResourcePolicy=json.dumps(pol),
    #   BlockPublicPolicy=True|False
    # )