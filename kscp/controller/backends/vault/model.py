from os import environ

from controller.exceptions import KSCPException
from controller.models.externalsecrets import ExternalSecret

class VaultSecret(ExternalSecret):
  def __init__(self, name, namespace, mount_point, path, values = {}, max_versions = 0):
    super().__init__(name, namespace, "vault", f"{ mount_point }/{ path }", values, { "max_versions": max_versions })

    self.__mount_point = mount_point
    self.__max_versions = max_versions


  def get_mount_point_and_path(self):
    return self.__mount_point, super().get_path()


  def get_path(self):
    return f"{ self.__mount_point }/{ super().get_path() }"

  
  def as_dict(self):
    ext = super().as_dict()
    ext.update({
      'max_versions': self.__max_versions
    })

    return ext


  def get_backend(self):
    return "vault"


  def compare_spec(self, spec):
    is_super_same = super().compare_spec(spec)

    if not is_super_same:
      return False
    
    return self.__mount_point == spec.get('')


  def clone(self, masked = True):
    return VaultSecret(
      super().get_name(),
      super().get_namespace(),
      self.__mount_point,
      super().get_path(),
      super().get_values() if not masked else super().get_masked_values(),
      self.__max_versions
    )
