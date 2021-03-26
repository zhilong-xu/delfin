import ast
import json

from oslo_log import log
from delfin.common import constants

from delfin.drivers.ibm.a9000r import rest_volume
from delfin.drivers import driver

LOG = log.getLogger(__name__)


# 卷
class UnityVolume(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rest_volume = rest_volume.RestVolume(**kwargs)
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
                volume_dict["status"] = constants.VolumeStatus.AVAILABLE
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

    def get_storage(self, context):
        # system_info = self.rest_handler.get_storage()
        # capacity = self.rest_handler.get_capacity()
        # version_info = self.rest_handler.get_soft_version()
        # status = constants.StorageStatus.OFFLINE
        # if system_info is not None and capacity is not None:
        #     system_entries = system_info.get('entries')
        #     for system in system_entries:
        #         content = system.get('content', {})
        #         name = content.get('name')
        #         model = content.get('model')
        #         serial_number = content.get('serialNumber')
        #         health_value = content.get('health').get('value')
        #         if health_value in UnityStorDriver.HEALTH_OK:
        #             status = constants.StorageStatus.NORMAL
        #         else:
        #             status = constants.StorageStatus.ABNORMAL
        #         break
        #     capacity_info = capacity.get('entries')
        #     for per_capacity in capacity_info:
        #         content = per_capacity.get('content', {})
        #         free = content.get('sizeFree')
        #         total = content.get('sizeTotal')
        #         used = content.get('sizeUsed')
        #         subs = content.get('sizeSubscribed')
        #         break
        #     soft_version = version_info.get('entries')
        #     for soft_info in soft_version:
        #         content = soft_info.get('content', {})
        #         version = content.get('id')
        #         break
        #     system_result = {
        #         'name': name,
        #         'vendor': 'DELL EMC',
        #         'model': model,
        #         'status': status,
        #         'serial_number': serial_number,
        #         'firmware_version': version,
        #         'location': '',
        #         'subscribed_capacity': int(subs),
        #         'total_capacity': int(total),
        #         'raw_capacity': int(total),
        #         'used_capacity': int(used),
        #         'free_capacity': int(free)
        #     }
        # return system_result
        pass

    def list_alerts(self, context, query_para=None):
        # page_number = 1
        # alert_model_list = []
        # while True:
        #     alert_list = self.rest_handler.get_all_alerts(page_number)
        #     if 'entries' not in alert_list:
        #         break
        #     if len(alert_list['entries']) < 1:
        #         break
        #     alert_handler.AlertHandler() \
        #         .parse_queried_alerts(alert_model_list, alert_list, query_para)
        #     page_number = page_number + 1
        # return alert_model_list
        pass

    def list_controllers(self, context):
        pass

    def list_disks(self, context):
        pass

    def list_ports(self, context):
        pass

    def list_storage_pools(self, context):
        # pool_info = self.rest_handler.get_all_pools()
        # pool_list = []
        # pool_type = constants.StorageType.UNIFIED
        # if pool_info is not None:
        #     pool_entries = pool_info.get('entries')
        #     for pool in pool_entries:
        #         content = pool.get('content', {})
        #         health_value = content.get('health').get('value')
        #         if health_value in UnityStorDriver.HEALTH_OK:
        #             status = constants.StorageStatus.NORMAL
        #         else:
        #             status = constants.StorageStatus.ABNORMAL
        #         pool_result = {
        #             'name': content.get('name'),
        #             'storage_id': self.storage_id,
        #             'native_storage_pool_id': str(content.get('id')),
        #             'description': content.get('description'),
        #             'status': status,
        #             'storage_type': pool_type,
        #             'total_capacity': int(content.get('sizeTotal')),
        #             'subscribed_capacity': int(content.get('sizeSubscribed')),
        #             'used_capacity': int(content.get('sizeUsed')),
        #             'free_capacity': int(content.get('sizeFree'))
        #         }
        #         pool_list.append(pool_result)
        # return pool_list
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    def reset_connection(self, context, **kwargs):
        # self.rest_handler.logout()
        # self.rest_handler.verify = kwargs.get('verify', False)
        # self.rest_handler.login()
        pass
