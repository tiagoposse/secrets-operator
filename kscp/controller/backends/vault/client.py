import hvac
import logging
import os

from controller.exceptions import KSCPException

logger = logging.getLogger('tool')

def get_vault_client() -> hvac.Client:
    addr = os.environ['VAULT_ADDR']
    logger.debug(f"Setting up vault connection to { addr }")

    token = "/vault/secrets/token"
    if token is None:
        raise Exception(
            "Please specify a path to the vault token either via --token or $VAULT_TOKEN"
        )

    with open(token, "r") as f:
        token = f.read().rstrip()

    client = hvac.Client(url=addr, token=token)
    if client.is_authenticated():
        return client
    else:
        raise KSCPException(500, "Authentication to vault unsuccessful")


# def __login_approle(self):
#   pass

# def __login_kubernetes(self):
#   pass

# def __login_token(self):
#   pass