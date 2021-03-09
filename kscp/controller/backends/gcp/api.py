import json

from os import environ
from google.cloud import secretmanager


def get_api_instance():
  return GCPBackend()

class GCPBackend:
  def __init__(self):
    self.__client = secretmanager.SecretManagerServiceClient()
    self.__project_id = f"{ environ.get('GCP_PROJECT_ID') }"


  def create_secret(self, name, namespace, spec) -> str:
    '''
      Process the creation of an gcpsecrets resource
    '''

    # Build a dict of settings for the secret
    secret = {'replication': {'automatic': {}}}
    secret_name = spec.get('path')

    # Create the secret
    self.__client.create_secret(
      secret_id=secret_name,
      parent=f"projects/{ self.__project_id }",
      secret=secret
    )

    path = self.__client.secret_path(self.__project_id, secret_name)
    self.__add_secret_version(
      path,
      spec.get('values')
    )

    return path


  def get_secret(self, spec) -> dict:
    '''
      Get the secret from the backend and return as json
    '''

    path = self.__client.secret_path(self.__project_id, spec.get('path'))

    response = self.__client.access_secret_version(request={"name": f"{ path }/versions/latest" })
    return json.loads(response.payload.data.decode("UTF-8"))


  def delete_secret(self, name, namespace, spec):
    '''
      Process the deletion of an gcpsecrets resource
    '''
    path = self.__client.secret_path(self.__project_id, spec.get('path'))

    self.__client.delete_secret(request={"name": path})


  def update_secret(self, name, namespace, __trigger_move, __trigger_value_change, old_spec, new_spec):
    '''
      Process the update of an gcpsecrets resource
    '''

    if __trigger_move:
      self.delete_secret(name, namespace, old_spec)
      self.create_secret(name, namespace, new_spec)
    elif __trigger_value_change:
      path = self.__client.secret_path(self.__project_id, new_spec.get('path'))
      self.__add_secret_version(path, new_spec.get('values'))


  def __add_secret_version(self, path, payload):
      '''
      Create a new version for the secret using the new values
      '''

      response = self.__client.add_secret_version(
          request={"parent": path, "payload": {"data": json.dumps(payload).encode('utf-8') }}
      )

      # Print the new secret version name.
      print(f'Added secret version: {response.name}')


  def grant_access(self, s_account, name, namespace, policies):
      '''
      Grant the given member access to a secret.
      '''

      resource_name = self.__client.secret_path(self.__project_id, f"{ namespace }-{ name }")

      policy = self.__client.get_iam_policy(request={"resource": resource_name})
      policy.bindings.add(role="roles/secretmanager.secretAccessor", members=[s_account])
      self.__client.set_iam_policy(request={"resource": resource_name, "policy": policy})

      # Print data about the secret.
      print("Updated IAM policy on {}".format(name))


  def revoke_access(self, s_account, name, namespace):
      '''
      Revoke the given member access to a secret.
      '''
    
      resource_name = self.__client.secret_path(self.__project_id, f"{ namespace }-{ name }")

      policy = self.__client.get_iam_policy(request={"resource": resource_name})

      # Remove the given member's access permissions.
      accessRole = "roles/secretmanager.secretAccessor"
      for b in list(policy.bindings):
        if b.role == accessRole and s_account in b.members:
          b.members.remove(s_account)

      new_policy = self.__client.set_iam_policy(request={"resource": resource_name, "policy": policy})

      # Print data about the secret.
      print("Updated IAM policy on {}".format(resource_name))
