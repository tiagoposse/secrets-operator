
from controller.models.externalsecrets import ExternalSecret

class AWSSecret(ExternalSecret):

  def __init__(self, name, namespace, path = None, values = {}, max_versions = 0):
    super().__init__(name, namespace, path, values, { max_versions })


  def get_backend(self):
    return "aws"