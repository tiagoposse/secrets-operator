import kopf
import logging

from controller.exceptions import KSCPException

logger = logging.getLogger()
logger.setLevel('DEBUG')

@kopf.on.create('externalsecrets.kscp.io')
def create_secret(name, namespace, spec, memo, patch, annotations, **_):
  '''
    Process the creation of an externalsecrets resource
  '''

  if annotations.get('kscp.io/manual-secret') in ['true', 'True', 'TRUE']:
    return True

  try:
    original_secret = memo.s_controller.get_object_for_backend(name, namespace, spec.get('backend'), spec.get('path'), spec.get('values'))
    created_secret = memo.s_controller.create_secret(original_secret)

    clone = created_secret.clone(True).get_spec()
    patch['spec'] = clone

  except KSCPException as e:
    raise kopf.PermanentError(str(e))


@kopf.on.delete('externalsecrets.kscp.io')
def delete_secret(name, namespace, spec, memo, **_):
  '''
    Process the deletion of an externalsecrets resource
  '''

  secret = memo.s_controller.get_object_for_backend(name, namespace, spec.get('backend'), spec.get('path'))
  memo.s_controller.delete_secret(secret)

@kopf.on.update('externalsecrets.kscp.io')
def update_secret(name, namespace, memo, old, new, patch, **_):
  '''
    Process the update of an externalsecrets resource
  '''

  try:
    old_secret = memo.s_controller.get_object_for_backend(name, namespace, old.get('spec').get('backend'), old.get('spec').get('path'), old.get('spec').get('values').copy())
    new_secret = memo.s_controller.get_object_for_backend(name, namespace, new.get('spec').get('backend'), new.get('spec').get('path'), new.get('spec').get('values').copy())
    
    new_secret = memo.s_controller.update_secret(old_secret, new_secret)

    clone = new_secret.clone(True).get_spec()
    patch['spec'] = clone if not clone.compare_spec(old_secret.get_spec()) else {}
  except KSCPException as e:
    raise kopf.PermanentError(str(e))
