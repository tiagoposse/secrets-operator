
from controller.models.externalsecrets import ExternalSecret

class GCPSecret(ExternalSecret):

  def __init__(self, name, namespace, path = None, values = {}, config = {}):
    super().__init__(name, namespace, "gcp", path, values, config)
