import kopf

@kopf.on.create('secretbindings.kscp.io')
def create_secret_binding(name, namespace, spec, memo, **_):
  '''
    Process the creation of a secretbindings resource
  '''
  
  memo.sb_controller.create_secret_binding(name, namespace, spec)


@kopf.on.delete('secretbindings.kscp.io')
def delete_secret_binding(name, namespace, spec, memo, **_):
  '''
    Process the deletion of a secretbindings resource
  '''

  memo.sb_controller.delete_secret_binding(name, namespace, spec)


@kopf.on.update('secretbindings.kscp.io', field="spec")
def update_secret_binding(name, namespace, new, old, memo, **_):
  '''
    Process the update of a secretbindings resource
  '''

  memo.sb_controller.update_secret_binding(name, namespace, new, old)

