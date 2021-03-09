import boto3
import json

from os import environ
from controller.backends.model import AWSSecret

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


  def get_object(self, name, namespace, path, values, config):
    return AWSSecret(name, namespace, "aws", path, values, **config)
  

  def create_secret(self, secret: AWSSecret):
    '''
      Process the creation of an awssecrets resource
    '''

    self.__client.create_secret(
      Name=secret.get_path(),
      SecretBinary=json.dumps(secret.get_creation_values()).encode('utf-8')
    )

  def delete_secret(self, secret: AWSSecret):
    '''
      Process the deletion of an awssecrets resource
    '''

    self.__client.delete_secret(
      RecoveryWindowInDays=7,
      SecretId=secret.get_path()
    )

  
  def update_secret(self, __trigger_value_change: bool, old_secret: AWSSecret, new_secret: AWSSecret):
    '''
      Process the update of a vaultsecrets resource
    '''

    if old_secret.get_path() != new_secret.get_path():
      self.delete_secret(old_secret)
      self.create_secret(new_secret)

    elif __trigger_value_change:
      self.__client.put_secret_value(
        SecretId=new_secret.get_path(),
        SecretBinary=json.dumps(new_secret.get_creation_values()).encode('utf-8')
      )

    return True


  def get_secret(self, secret: AWSSecret):
    return json.loads(self.__client.get_secret_value(
      SecretId=secret.get_path()
    ).SecretBinary.decode('utf-8'))


  # def grant_access(self, s_account, name, namespace):
  #   pol = aws_policy_template.copy()
  #   pol['Statement']['Principal']['AWS'] += f"{ self.__aws_account_id }:{ s_account }"
    
  #   self.__client.put_resource_policy(
  #     SecretId=name,
  #     ResourcePolicy=json.dumps(pol),
  #     BlockPublicPolicy=True|False
  #   )


  # def revoke_access(self, s_account, name, namespace):
  #   pass
  #   # pol = aws_policy_template.copy()
  #   # pol['Statement']['Principal']['AWS'] += f"{ __aws_account_id }:{ s_account }"

  #   # self.__client.put_resource_policy(
  #   #   SecretId=name,
  #   #   ResourcePolicy=json.dumps(pol),
  #   #   BlockPublicPolicy=True|False
  #   # )