import importlib
import kubernetes
import logging
import sys

from os import environ, path
sys.path.append(path.join(path.dirname(path.abspath(__file__)), "../"))

from controller.models.secretbindings import SecretBinding
from controller.models.secretpolicies import SecretPolicy
from controller.models.externalsecrets import ExternalSecret
from controller.backends.k8s.api import KubernetesBackend
from controller.exceptions import KSCPException

logger = logging.getLogger()


class KSCPEngine:
  __clients = None
  __backends = []

  def __init__(self, backends: list = None):
    logger.info("Creating controller...")

    self.__backends = environ.get('KSCP_BACKENDS').split(',') if backends is None else backends

    self.__clients = {
      'k8s': KubernetesBackend()
    }

    logger.info(f"Loading backends: { ','.join(self.__backends) }")

    for backend in self.__backends:
      api = importlib.import_module(f"controller.backends.{ backend }.api")
      
      try:
        self.__clients[backend] = api.get_api_instance()
      except KSCPException as e:
        logger.error(e)
        exit(1)

    self.__allow_by_default = environ.get('ALLOW_BY_DEFAULT') in ['True', 'true', 'TRUE']

    logger.info("Controller created.")


  def get_backend_client(self, backend):
    return self.__clients.get(backend)


  def can_access_secret(self, secret: ExternalSecret):
    for spec in self.__clients.get('k8s').list_crd('secretpolicies', secret.get_namespace()):
      if not SecretPolicy(
            spec.get('name'),
            spec.get('namespace'),
            spec.get('allow'),
            spec.get('reject')
          ).check_path_allowed(secret.get_path()):
        return False

    return self.__allow_by_default