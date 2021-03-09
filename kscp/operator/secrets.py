import kopf

@kopf.on.create('externalsecrets.kscp.io')
def create_secret(name, namespace, spec, memo, patch, **_):
  '''
    Process the creation of an externalsecrets resource
  '''

  patch['spec'] = {
    'path': memo.s_controller.create_secret(name, namespace, spec)
  }


@kopf.on.delete('externalsecrets.kscp.io')
def delete_secret(name, namespace, spec, memo, **_):
  '''
    Process the deletion of an externalsecrets resource
  '''

  memo.s_controller.delete_secret(name, namespace, spec)

@kopf.on.update('externalsecrets.kscp.io')
def update_secret(name, namespace, memo, old, new, diff, **_):
  '''
    Process the update of an externalsecrets resource
  '''
  
  memo.s_controller.update_secret(name, namespace, old.get('spec'), new.get('spec'), diff)
