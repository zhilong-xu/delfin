import ast
import json

from oslo_log import log
from delfin.common import constants

from delfin.drivers.ibm.a9000r import rest_volume, ssh_volume
from delfin.drivers import driver

LOG = log.getLogger(__name__)


# 卷
class UnityVolume(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rest_volume = rest_volume.RestVolume(**kwargs)
        self.ssh_volume = ssh_volume.SSHVolume(**kwargs)
        self.rest_volume.login()

    # 列示卷
    def list_volumes(self, context):
        volume = dict()
        volume_dict = dict()
        # 请求查询接口
        volumes = self.rest_volume.get_all_rest_volumes(self)
        self.volume_handler(volumes, volume_dict, volume)
        return volume

    def volume_handler(self, volumes, volume_dict, volume):
        if volumes is not None:
            volumeStr = volumes.get('volume')
            if volumeStr is not None and any(volumeStr):
                volume_dict["name"] = volumeStr.get("name")
                volume_dict["storage_id"] = self.storage_id
                # 无法获取，这里会是空
                volume_dict["description"] = volumeStr.get("description")
                volume_dict["status"] = constants.ControllerStatus.NORMAL
                volume_dict["native_volume_id"] = volumeStr.get("id")
                volume_dict["native_storage_pool_id"] = volumeStr.get("pool")
                volume_dict["type"] = constants.VolumeType.THICK

                # 需要计算的
                totalCapacity = volumeStr.get("size")
                volume_dict["total_capacity"] = totalCapacity
                usedCapacity = volumeStr.get("used_capacity")
                volume_dict["used_capacity"] = usedCapacity
                free_capacity = int(totalCapacity) - int(usedCapacity)
                volume_dict["free_capacity"] = free_capacity
        volume["volume"] = volume_dict

    def add_trap_config(self, context, trap_config):
        pass

    def clear_alert(self, context, alert):
        # return self.rest_handler.remove_alert(alert)
        pass

    # 系统
    def get_storage(self, context):
        # 通过https请求调用返回数据
        system_info = self.rest_volume.get_storage()
        # 开始封装数据
        storage_system = dict()
        system = dict()
        if system_info is not None and any(system_info):
            systemObject = system_info.get("system")
            system["name"] = systemObject.get("name")
            system["vender"] = self.storage_id
            # 这里会使空，无法获取
            system["description"] = systemObject.get("description")
            system["model"] = systemObject.get("safe_mode")
            status = constants.ControllerStatus.NORMAL if systemObject.get('system_state') == 'on' \
                else constants.ControllerStatus.OFFLINE
            system["status"] = status
            # 这里会使空，无法获取
            system["location"] = systemObject.get("location")
            # 这里会使空，无法获取
            system["raw_capacity"] = systemObject.get("raw_capacity")
            physicalSize = systemObject.get("physical_size")
            system["total_capacity"] = physicalSize
            physicalFree = systemObject.get("physical_free")
            system["free_capacity"] = physicalFree
            # 相减计算used_capacity
            system["used_capacity"] = int(physicalSize) - int(physicalFree)

        # cli 获取的字段
        system["serial_number"] = self.ssh_volume.get_storage_serial_number()
        system["version_get"] = self.ssh_volume.get_storage_version_get()
        # system 放进 storage_system
        storage_system["system"] = system
        return storage_system

    def list_alerts(self, context, query_para=None):
        pass

    def list_controllers(self, context):
        pass

    def list_disks(self, context):
        pass

    def list_ports(self, context):
        pass

    # 池
    def list_storage_pools(self, context):
        pool_info = self.rest_volume.get_all_pools()
        pool_Object = dict()
        pool = dict()
        if pool_info is not None and any(pool_info):
            pool_return = pool_info.get("pool")
            pool["name"] = pool_return.get("name")
            pool["storage_id"] = self.storage_id
            pool["native_storage_pool_id"] = pool_return.get("id")
            # description 暂时无法获取 会为None
            pool["description"] = pool_return.get("description")
            pool["status"] = constants.ControllerStatus.NORMAL
            pool["storage_type"] = constants.StorageType.BLOCK
            # 需要计算的
            total_capacity = pool_return.get("size")
            pool["total_capacity"] = total_capacity
            used_by_volumes = pool_return.get("used_by_volumes")
            pool["used_capacity"] = used_by_volumes
            pool["free_capacity"] = int(total_capacity) - int(used_by_volumes)
        pool_Object["pool"] = pool
        return pool_Object

    def remove_trap_config(self, context, trap_config):
        pass

    def reset_connection(self, context, **kwargs):
        # self.rest_handler.logout()
        # self.rest_handler.verify = kwargs.get('verify', False)
        # self.rest_handler.login()
        pass

    def list_quotas(self, context):
        pass

    def list_filesystems(self, context):
        pass

    def list_qtrees(self, context):
        pass

    def list_shares(self, context):
        pass
