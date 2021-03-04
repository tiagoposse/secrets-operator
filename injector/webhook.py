import base64
import copy
import json
import re

from flask import current_app
from jsonpatch import JsonPatch
from os import environ


__INJECTION_ANNOTATION = 'secrets.kscp.io/inject-bindings'
__INJECTION_TEMPLATE_ANNOTATION = 'secrets.kscp.io/inject-template-([\w\-\_]+)'
__INJECTION_TARGET_ANNOTATION = 'secrets.kscp.io/inject-target-([\w\-\_]+)'
__INIT_FIRST_ANNOTATION = 'secrets.kscp.io/init-first'
__SKIP_ANNOTATION = 'secrets.kscp.io/injected'

__DEFAULT_MOUNT_PATH = '/kscp/secrets'

__default_volume = {
  "name": "kscp-secrets",
  "emptyDir": {}
}

def get_vault_secret_path(name, vault_spec):
    path = vault_spec.get('spec').get('mountPoint')
    if vault_spec.get('spec').get('path') is None:
      path = f"{ path }/{ name }"
    else:
      path = f"{ path }/{ vault_spec.get('spec').get('path') }"
    
    return path


def get_env_for_init_container(use_vault, use_aws, use_gcp):
  env = [
    { 'name': 'USE_VAULT', 'value': str(use_vault) },
    { 'name': 'USE_GCP', 'value': str(use_gcp) },
    { 'name': 'USE_AWS', 'value': str(use_aws) }
  ]

  if use_vault:
    env += [
      { 'name': 'VAULT_ADDR', 'value': environ.get('VAULT_ADDR') },
    ]

  if use_gcp:
    env.append({ 'name': 'GCP_PROJECT_ID', 'value': environ.get('GCP_PROJECT_ID') })

  if use_aws:
    env += [
      { 'name': 'AWS_ACCOUNT_ID', 'value': environ.get('AWS_ACCOUNT_ID') },
      { 'name': 'AWS_REGION', 'value': environ.get('AWS_REGION') }
    ]

  return env


def get_init_container(env, volume_mounts):
  initContainer = {
    "name": "kscp-retrieve-secrets",
    "image": environ.get('INIT_IMAGE'),
    'imagePullPolicy': 'Always',
    "env": env,
    "volumeMounts": volume_mounts
  }

  return initContainer


def process_annotations(injector, annotations, namespace):
  inject_bindings = {}
  inject_binding_templates = {}
  inject_binding_targets = {}

  current_app.logger.debug("Processing annotations")
  for annotation_name, annotation_value in annotations.items():
    inject_match = re.match(rf"{ __INJECTION_ANNOTATION }", annotation_name)

    if inject_match:
      for bind in annotation_value.split(','):
        inject_bindings[bind] = injector.get_secret_binding(bind, namespace)
      
      continue

    template_inject_match = re.match(rf"{ __INJECTION_TEMPLATE_ANNOTATION }", annotation_name)
    if template_inject_match:
      inject_binding_templates[template_inject_match.group(1)] = annotation_value
      continue

    target_inject_match = re.match(rf"{ __INJECTION_TARGET_ANNOTATION }", annotation_name)
    if target_inject_match:
      inject_binding_targets[target_inject_match.group(1)] = annotation_value
      continue

  return [ {
    'name': k,
    'obj': v,
    'template': inject_binding_templates.get(k),
    'target': inject_binding_targets.get(k)
   } for k, v in inject_bindings.items()]


def get_target_and_volume_info(bind):
  if bind.get('target') is None:
    return f"{ __DEFAULT_MOUNT_PATH }/{ bind.get('name') }", [], []
  elif bind.get('target').count('/') == 1:
    return f"{ __DEFAULT_MOUNT_PATH }/{ bind.get('target') }", [], []
  
  return (
    bind.get('target'),
    [{
      'name': f"kscp-secrets-{ bind.get('name') }",
      'emptyDir': {}
    }],
    [{
      "name": f"kscp-secrets-{ bind.get('name') }",
      "mountPath": '/'.join(bind.get('target').split('/')[0:-1])
    }]
  )
      
def process_binds(injector, namespace, raw_binds):
  init_env = []
  init_volumes = []
  
  init_volume_mounts = []
  use_default_volume = False
  secrets = {
    'vault': [],
    'gcp': [],
    'aws': []
  }

  for bind in raw_binds:
    # current_app.logger.debug(bind.get('obj'))
    # current_app.logger.debug(bind.get('name'))
    # current_app.logger.debug(bind.get('template'))
    # current_app.logger.debug(bind.get('target'))

    # get secret names for this bind
    for secret in bind.get('obj').get('spec').get('secrets'):
        if secret.get('backend') != 'vault':
          path = secret.get('name') 
        else:
          path = get_vault_secret_path(
            secret.get('name'),
            injector.get_vaultsecret_spec(
              secret.get('name'),
              namespace
            )
          )
        
        secrets[secret.get('backend')].append(path)


    target, add_init_volumes, add_init_volume_mounts = get_target_and_volume_info(bind)
    bind['target'] = target

    if len(add_init_volumes) > 0:
      init_volumes += add_init_volumes
      init_volume_mounts += add_init_volume_mounts
    else:
      use_default_volume = True

    # Add this bind to the env of the init container
    init_env.append({
      'name': f"BIND_{ bind.get('name') }",
      'value': json.dumps(injector.get_bind_conf(
        bind,
        namespace,
        secrets['vault'],
        secrets['aws'],
        secrets['gcp']
      ))
    })

  # Add base config for the init container here
  init_env += get_env_for_init_container(
    len(secrets['vault']) > 0,
    len(secrets['aws']) > 0,
    len(secrets['gcp']) > 0
  )

  if use_default_volume:
    init_volumes.append(__default_volume)
    init_volume_mounts += [
      {
        "name": 'kscp-secrets',
        "mountPath": __DEFAULT_MOUNT_PATH
      }
    ]
  
  return init_env, init_volume_mounts, init_volumes


def mutate(injector, req):
  patch = ""

  if req["operation"] != "CREATE":
    return True, ""
    
  modified_spec = copy.deepcopy(req)
  object_metadata = modified_spec["object"]["metadata"]

  if (object_metadata.get('annotations') is None or 
        object_metadata["annotations"].get(__SKIP_ANNOTATION) in [ 'true', 'True' ]):
      return True, ""
  
  # Get bind objects to inject
  raw_binds = process_annotations(
    injector,
    object_metadata["annotations"],
    object_metadata["namespace"]
  )
  if len(raw_binds) == 0:
    return True, ""

  init_container_env, container_vms, pod_vols = process_binds(injector, object_metadata["namespace"], raw_binds)

  # Add our init container
  if 'initContainers' not in modified_spec["object"]['spec']:
    modified_spec["object"]['spec']['initContainers'] = []

  modified_spec["object"]['spec']['initContainers'].append(get_init_container(
    init_container_env, container_vms
  ))

  current_app.logger.debug("init containers:")
  current_app.logger.debug(modified_spec["object"]['spec']['initContainers'])

  # Add our secret volumes
  if 'volumes' not in modified_spec["object"]['spec']:
    modified_spec["object"]['spec']['volumes'] = []

  modified_spec["object"]['spec']['volumes'] += pod_vols

  # Add volumeMounts to every container
  for index in range(0, len(modified_spec["object"]['spec']['containers'])):
    if 'volumeMounts' not in modified_spec["object"]['spec']['containers'][index]:
      modified_spec["object"]['spec']['containers'][index]['volumeMounts'] = []
      
  modified_spec["object"]['spec']['containers'][index]['volumeMounts'] += container_vms

  patch = JsonPatch.from_diff(req["object"], modified_spec["object"])

  return True, base64.b64encode(str(patch).encode()).decode()