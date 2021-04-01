import paramiko
import six
from oslo_log import log
from delfin import exception, utils
from delfin.drivers.utils.ssh_client import SSHClient, SSHPool

LOG = log.getLogger(__name__)


class SSHHandler(object):
    # 显示配置参数的值
    CONFIG_GET = 'config_get [ name=machine_serial_number ]'
    # 打印系统的当前版本
    VERSION_GET = 'version_get'

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.ssh_pool = SSHPool(**kwargs)

    def login(self):
        try:
            with self.ssh_pool.item() as ssh:
                SSHHandler.do_exec('lssystem', ssh)
        except Exception as e:
            LOG.error("Failed to login ibm a9000r %s" %
                      (six.text_type(e)))
            raise e

    # 显示配置参数的值 machine_serial_number的获取
    def get_storage_serial_number(self):
        serialNumber = None
        try:
            serialNumber = self.exec_ssh_command(SSHHandler.CONFIG_GET)
        except Exception as e:
            LOG.error("Get all storage machine_serial_number error: %s", six.text_type(e))
        return serialNumber

    # 可打印系统的当前版本  firmware_version字段获取
    def get_storage_version_get(self):
        firmwareVersion = None
        try:
            # ssh_client = SSHClient(**self.kwargs)
            # firmwareVersion = ssh_client.do_exec(SSHHandler.VERSION_GET)
            firmwareVersion = self.exec_ssh_command(SSHHandler.VERSION_GET)
        except Exception as e:
            LOG.error("Get all storage firmware_version error: %s", six.text_type(e))
        return firmwareVersion

    def exec_ssh_command(self, command):
        try:
            with self.ssh_pool.item() as ssh:
                ssh_info = SSHHandler.do_exec(command, ssh)
            return ssh_info
        except Exception as e:
            msg = "Failed to ssh ibm a9000r ssh_handler %s: %s" % \
                  (command, six.text_type(e))
            raise exception.SSHException(msg)

    def exec_ssh_command(self, command):
        try:
            with self.ssh_pool.item() as ssh:
                ssh_info = SSHHandler.do_exec(command, ssh)
            return ssh_info
        except Exception as e:
            msg = "Failed to ssh ibm storwize_svc %s: %s" % \
                  (command, six.text_type(e))
            raise exception.SSHException(msg)

    @staticmethod
    def do_exec(command_str, ssh):
        """Execute command"""
        try:
            utils.check_ssh_injection(command_str)
            if command_str is not None and ssh is not None:
                stdin, stdout, stderr = ssh.exec_command(command_str)
                res, err = stdout.read(), stderr.read()
                re = res if res else err
                result = re.decode()
        except paramiko.AuthenticationException as ae:
            LOG.error('doexec Authentication error:{}'.format(ae))
            raise exception.InvalidUsernameOrPassword()
        except Exception as e:
            err = six.text_type(e)
            LOG.error('doexec InvalidUsernameOrPassword error')
            if 'timed out' in err:
                raise exception.SSHConnectTimeout()
            elif 'No authentication methods available' in err \
                    or 'Authentication failed' in err:
                raise exception.InvalidUsernameOrPassword()
            elif 'not a valid RSA private key file' in err:
                raise exception.InvalidPrivateKey()
            else:
                raise exception.SSHException(err)
        return result
