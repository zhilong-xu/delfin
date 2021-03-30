import six
from oslo_log import log

from delfin.drivers.utils.ssh_client import SSHClient

LOG = log.getLogger(__name__)


class SSHVolume(object):
    # 显示配置参数的值
    CONFIG_GET = 'config_get [ name=machine_serial_number ]'
    # 打印系统的当前版本
    VERSION_GET = 'version_get'

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    # 显示配置参数的值 machine_serial_number的获取
    def get_storage_serial_number(self):
        serialNumber = None
        try:
            ssh_client = SSHClient(**self.kwargs)
            serialNumber = ssh_client.do_exec(SSHVolume.CONFIG_GET)
        except Exception as e:
            LOG.error("Get all storage machine_serial_number error: %s", six.text_type(e))
        return serialNumber

    # 可打印系统的当前版本  firmware_version字段获取
    def get_storage_version_get(self):
        firmwareVersion = None
        try:
            ssh_client = SSHClient(**self.kwargs)
            firmwareVersion = ssh_client.do_exec(SSHVolume.VERSION_GET)
        except Exception as e:
            LOG.error("Get all storage firmware_version error: %s", six.text_type(e))
        return firmwareVersion
