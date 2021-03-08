import base64
import copy
from injector.initcontainer import InitContainer
import re
from typing import Tuple

from flask import current_app
from jsonpatch import JsonPatch
from os import environ


__INJECTION_ANNOTATION = 'secrets.kscp.io/inject-bindings'
__INJECTION_TEMPLATE_ANNOTATION = 'secrets.kscp.io/inject-template-([\w\-\_]+)'
__INJECTION_TARGET_ANNOTATION = 'secrets.kscp.io/inject-target-([\w\-\_]+)'
__INIT_FIRST_ANNOTATION = 'secrets.kscp.io/init-first'
__SKIP_ANNOTATION = 'secrets.kscp.io/injected'

__DEFAULT_MOUNT_PATH = '/kscp/secrets'
__DEFAULT_VOLUME = {
  "name": "kscp-secrets",
  "emptyDir": {}
}

def get_target_for_bind(bind, spec) -> Tuple[str, bool]:
  '''
    Return the target path for this bind to be rendered and whether
    the default mount path is used, triggering the addition of the volume
  '''

  if bind.get('target') is not None:
    if bind.get('target').count('/') == 1:
      return f"{ __DEFAULT_MOUNT_PATH }/{ bind.get('target') }", True
    
    return bind.get('target'), False

  if spec.get('target') is not None:
    if spec.get('target').count('/') == 1:
      return f"{ __DEFAULT_MOUNT_PATH }/{ spec.get('target') }", True
    
    return spec.get('target'), False

  # default
  return f"{ __DEFAULT_MOUNT_PATH }/{ bind.get('name') }", True

def get_bind_names_from_annotations(annotations):
  inject_bindings = {}
  inject_binding_templates = {}
  inject_binding_targets = {}

  current_app.logger.debug("Processing annotations")
  for annotation_name, annotation_value in annotations.items():

    if annotation_name == __INJECTION_ANNOTATION:
      inject_bindings = annotation_value.split(',')
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
    'name': bind,
    'obj': None,
    'template': inject_binding_templates.get(bind),
    'target': inject_binding_targets.get(bind)
   } for bind in inject_bindings]


def should_mutate(annotations):
  return annotations is not None or annotations.get(__SKIP_ANNOTATION) not in [ 'true', 'True', 'TRUE' ]

def mutate(controller, req):
  if req["operation"] != "CREATE" or not should_mutate(req["object"]["metadata"]['annotations']):
    return True, ""
    
  req_obj = copy.deepcopy(req).get('object')
  
  raw_binds = get_bind_names_from_annotations(req_obj.get('metadata').get('annotations'))
  if len(raw_binds) == 0:
    return True, ""

  initContainer = InitContainer('kscp-init', environ.get('INIT_IMAGE'))

  use_default_volume = False
  for bind in raw_binds:
    spec = controller.get_secretbinding_spec(
      bind.get('name'),
      req_obj.get('metadata').get('namespace')
    ).get('spec')

    bind['target'], use_default_path = get_target_for_bind(bind, spec)
    use_default_volume = use_default_volume or use_default_path

    initContainer.add_bind(bind, req_obj.get('metadata').get('namespace'), spec)

  renderedContainer = initContainer.get()
  # Add our init container
  if 'initContainers' not in req_obj['spec']:
    req_obj['spec']['initContainers'] = [renderedContainer]
  else:
    req_obj['spec']['initContainers'].append(renderedContainer)

  pod_vols = initContainer.get_volumes()
  if use_default_volume:
    pod_vols.append(__DEFAULT_VOLUME)

  # Add our secret volumes
  if 'volumes' not in req_obj['spec']:
    req_obj['spec']['volumes'] = pod_vols
  else:
    req_obj['spec']['volumes'] += pod_vols

  # Add volumeMounts to every container
  for index in range(0, len(req_obj['spec']['containers'])):
    if 'volumeMounts' not in req_obj['spec']['containers'][index]:
      req_obj['spec']['containers'][index]['volumeMounts'] = []
      
  req_obj['spec']['containers'][index]['volumeMounts'] += renderedContainer.get('volumeMounts')

  patch = JsonPatch.from_diff(req["object"], req_obj)

  return True, base64.b64encode(str(patch).encode()).decode()