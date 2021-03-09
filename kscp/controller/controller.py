import importlib
import kubernetes
import logging
import sys

from os import environ, path
sys.path.append(path.join(path.dirname(path.abspath(__file__)), "../"))

logger = logging.getLogger()

from controller.access import AccessEngine

class KSCPController:
  __clients = None
  __backends = []

  def __init__(self, backends: list = None):
    self.__backends = backends = environ.get('KSCP_BACKENDS').split(',') if backends is None else backends

    kubernetes.config.load_incluster_config()
    self.__clients = {
      'k8s': kubernetes.client.ApiClient()
    }

    for backend in backends:
      api = importlib.import_module(f"controller.backends.{ backend }.api")
      self.__clients[backend] = api.get_api_instance()

    self.__access = AccessEngine(
      self.__clients,
      environ.get('AUTH_BACKEND') in ['True', 'true', 'TRUE'],
      environ.get('ALLOW_BY_DEFAULT') in ['True', 'true', 'TRUE']
    )

  def get_backend_client(self, backend):
    return self.__clients.get(backend)

  def grant_access(self, name, namespace, spec):
    self.__access.grant_access(name, namespace, spec)

  def revoke_access(self, name, namespace, spec):
    self.__access.revoke_access(name, namespace, spec)
