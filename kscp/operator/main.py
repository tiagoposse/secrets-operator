import asyncio
import logging
import kopf
import sys

from os import path
sys.path.append(path.join(path.dirname(path.abspath(__file__)), "../"))

from controller.controller import KSCPController
from controller.crd_processors.secrets import SecretsController
from controller.crd_processors.secretbindings import SecretBindingsController
from controller.crd_processors.secretpolicies import SecretPoliciesController

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

@kopf.on.startup()
def configure(memo, **_):
  main_controller = KSCPController()
  memo.s_controller = SecretsController(main_controller)
  memo.sb_controller = SecretBindingsController(main_controller)
  memo.sp_controller = SecretPoliciesController(main_controller)

  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
