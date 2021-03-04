import kopf

from os import environ
from google.cloud import secretmanager

from utils import generate_secret_values, get_change_path

if environ.get('USE_AWS') in [ 'true', 'True', 'TRUE' ]:
  __project_id = environ.get('PROJECT_ID')
  __client = secretmanager.SecretManagerServiceClient()


@kopf.on.create('gcpsecrets.kscp.io')
def create_secret(name, namespace, spec, **_):
  '''
    Process the creation of an gcpsecrets resource
  '''

  parent = f"projects/{ __project_id }"

  # Build a dict of settings for the secret
  secret = {'replication': {'automatic': {}}}
  secret_name = f"{ namespace }-{ name }"

  # Create the secret
  __client.create_secret(
    secret_id=secret_name,
    parent=parent,
    secret=secret
  )

  add_secret_version(
    secret_name,
    parent,
    generate_secret_values(spec.get('values'))
  )


@kopf.on.delete('gcpsecrets.kscp.io')
def delete_secret(name, namespace, **_):
  '''
    Process the deletion of an gcpsecrets resource
  '''

  secret_name = f"{ namespace }-{ name }"
  resource_name = __client.secret_path(__project_id, secret_name)

  __client.delete_secret(request={"name": resource_name})


@kopf.on.update('gcpsecrets.kscp.io')
def update_secret(name, namespace, old, new, diff, **kwargs):
  '''
    Process the update of an gcpsecrets resource
  '''
  secret_name = f"{ namespace }-{ name }"

  values = read_gcp_secret(secret_name)

  for op, path, old_val, new_val in diff:
    change_path = get_change_path(path)

    if not change_path.startswith('.spec.values.'):
      continue

    if op == 'delete':
      del values[path[-1]]
    else:
      values[path[-1]] = new_val

  add_secret_version(
    secret_name,
    f"projects/{__project_id}",
    generate_secret_values(values)
  )



def add_secret_version(secret_id, project_id, payload):
    """
    Create a new version for the secret using the new values
    """

    response = __client.add_secret_version(
      parent=f"projects/{project_id}/secrets/{secret_id}",
      payload={ 'data': payload.encode('UTF-8') }
    )

    # Print the new secret version name.
    print(f'Added secret version: {response.name}')


def grant_gcp_access(s_account, name, namespace):
    """
    Grant the given member access to a secret.
    """

    resource_name = __client.secret_path(__project_id, f"{ namespace }-{ name }")

    policy = __client.get_iam_policy(request={"resource": resource_name})
    policy.bindings.add(role="roles/secretmanager.secretAccessor", members=[s_account])
    __client.set_iam_policy(request={"resource": resource_name, "policy": policy})

    # Print data about the secret.
    print("Updated IAM policy on {}".format(name))


def revoke_gcp_access(s_account, name, namespace):
    """
    Revoke the given member access to a secret.
    """
  
    resource_name = __client.secret_path(__project_id, f"{ namespace }-{ name }")

    policy = __client.get_iam_policy(request={"resource": resource_name})

    # Remove the given member's access permissions.
    accessRole = "roles/secretmanager.secretAccessor"
    for b in list(policy.bindings):
        if b.role == accessRole and s_account in b.members:
            b.members.remove(s_account)

    # Update the IAM Policy.
    new_policy = __client.set_iam_policy(request={"resource": resource_name, "policy": policy})

    # Print data about the secret.
    print("Updated IAM policy on {}".format(resource_name))
