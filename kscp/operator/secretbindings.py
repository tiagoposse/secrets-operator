import kopf

from controller.processors.secretbindings import SecretBindingsController

@kopf.on.create('secretbindings.kscp.io')
def create_secret_binding(name, namespace, spec, memo, **_):
  '''
    Process the creation of a secretbindings resource
  '''
  
  bind = SecretBindingsController.get_object(name, namespace, spec)
  memo.sb_controller.create_secret_binding(bind)


@kopf.on.delete('secretbindings.kscp.io')
def delete_secret_binding(name, namespace, spec, memo, **_):
  '''
    Process the deletion of a secretbindings resource
  '''

  bind = SecretBindingsController.get_object(name, namespace, spec)
  memo.sb_controller.delete_secret_binding(bind)


@kopf.on.update('secretbindings.kscp.io', field="spec")
def update_secret_binding(name, namespace, new, old, memo, **_):
  '''
    Process the update of a secretbindings resource
  '''

  memo.sb_controller.update_secret_binding(
    SecretBindingsController.get_object(name, namespace, old),
    SecretBindingsController.get_object(name, namespace, new)
  )