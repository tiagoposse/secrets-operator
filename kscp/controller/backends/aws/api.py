import boto3
import json

from os import environ

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

    self.__client.create_secret(
      Name=spec.get('path'),
      SecretBinary=json.dumps(spec.get('values')).encode('utf-8')
    )

    return spec.get('path')

  def delete_secret(self, name, namespace, spec):
    '''
      Process the deletion of an awssecrets resource
    '''

    self.__client.delete_secret(
      RecoveryWindowInDays=7,
      SecretId=spec.get('path'),
    )


  def update_secret(self, name, namespace, __trigger_move, __trigger_value_change, old_spec, new_spec):
    '''
      Process the update of an awssecrets resource
    '''

    values = self.read_secret(name)

    if __trigger_move:
      self.delete_secret(name, namespace, old_spec)
      self.create_secret(name, namespace, new_spec)
    elif __trigger_value_change:
      self.__client.put_secret_value(
        SecretId=f"{ namespace }-{ name }",
        SecretBinary=json.dumps(new_spec.get('values')).encode('utf-8')
      )


  def get_secret(self, name, namespace, spec):
    return json.loads(self.__client.get_secret_value(
      SecretId=spec.get('path')
    ).SecretBinary.decode('utf-8'))


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