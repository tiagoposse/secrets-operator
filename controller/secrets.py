# import boto3
# import kopf
# import logging


# if environ.get('USE_VAULT') in [ 'true', 'True', 'TRUE' ]:
#   from backends.vault.api import create_vault_secret, update_vault_secret, delete_vault_secret

# if environ.get('USE_AWS') in [ 'true', 'True', 'TRUE' ]:
# from backends.aws.api import create_aws_secret, update_aws_secret, delete_aws_secret

# if environ.get('USE_GCP') in [ 'true', 'True', 'TRUE' ]:
# from backends.gcp.api import create_gcp_secret, update_gcp_secret, delete_gcp_secret

# from google.cloud import secretmanager

# logger = logging.getLogger()

# @kopf.on.create('externalsecrets.kscp.io')
# def create_secret(name, spec, **kwargs):
#   '''
#     Process the creation of an externalsecrets resource
#   '''

#   values = spec.get('values')
#   if not values:
#     raise kopf.PermanentError(f"Values must be set. Got { values }.")

#   if spec.get('backend') == 'vault':
#     create_vault_secret(spec)
#   elif spec.get('backend') == 'aws':
#     create_aws_secret(name, spec)
#   elif spec.get('backend') == 'gcp':
#     create_gcp_secret(name, spec)
#   else:
#     raise Exception(f"Unsupported backend { spec.get('backend') }")

# @kopf.on.delete('externalsecrets.kscp.io')
# def delete_secret(name, spec, **kwargs):
#   '''
#     Process the deletion of an externalsecrets resource
#   '''
#   if spec.get('backend') == 'vault':
#     delete_vault_secret(
#       spec
#     )
#   elif spec.get('backend') == 'aws':
#     delete_aws_secret(
#       boto3.client('secretsmanager'),
#       name
#     )
#   elif spec.get('backend') == 'gcp':
#     delete_gcp_secret(
#       secretmanager.SecretManagerServiceClient(),
#       name
#     )
#   else:
#     raise Exception(f"Unsupported backend { spec.get('backend') }")

# @kopf.on.update('externalsecrets.kscp.io')
# def update_secret(old, new, diff, **kwargs):
#   '''
#     Process the update of an externalsecrets resource
#   '''
      
#   if new.get('spec').get('backend') == 'vault':
#     update_vault_secret(
#       get_vault_client(),
#       old,
#       new,
#       diff
#     )
#   elif new.get('spec').get('backend') == 'aws':
#     update_aws_secret(
#       boto3.client('secretsmanager'),
#       old,
#       new,diff
#     )
#   elif new.get('spec').get('backend') == 'gcp':
#     update_gcp_secret(
#       secretmanager.SecretManagerServiceClient(),
#       old,
#       new,
#       diff
#     )
#   else:
#     raise Exception(f"Unsupported backend { new.get('spec').get('backend') }")
