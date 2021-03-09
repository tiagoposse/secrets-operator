from controller.engine import KSCPEngine
from controller.processors.externalsecrets import ExternalSecretsController
from controller.processors.secretbindings import SecretBindingsController


def get_controllers():
  main_controller = KSCPEngine()

  return (
    ExternalSecretsController(main_controller),
    SecretBindingsController(main_controller)
  )