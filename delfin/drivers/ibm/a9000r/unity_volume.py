

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
        page_number = 1
        volume_list = []
        while True:
            # 请求查询接口
            luns = self.rest_handler.get_all_rest_volumes(self, page_number)
            if 'entries' not in luns:
                break
            if len(luns['entries']) < 1:
                break
            self.volume_handler(luns, volume_list)
            page_number = page_number + 1

        return volume_list
