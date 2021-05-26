import json
import platform

import six
from oslo_log import log
from delfin import cryptor
from delfin import exception
from delfin.common import constants
from delfin.drivers.hitachi.hus import consts
from delfin.drivers.utils.cli_client import NaviClient

LOG = log.getLogger(__name__)


class SSHHandler(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        cli_access = kwargs.get('rest')
        if cli_access is None:
            raise exception.InvalidInput('Input navicli_access is missing')
        self.navi_host = cli_access.get('host')
        self.navi_port = cli_access.get('port')
        self.navi_username = cli_access.get('username')
        self.navi_password = cli_access.get('password')
        # horcm0.conf文件中最后的数字
        # self.IH = cli_access.get('IH')
        self.IH = '0'

    # 登录
    def login(self):
        start = None
        if 'windows' == platform.system().lower():
            # 启动程序  horcmstart.exe
            start = consts.WINDOWS_HORCM_START.format(self.IH)
        elif 'linux' == platform.system().lower():
            start = consts.LINUX_HORCM_START.format(self.IH)
        success = NaviClient.execShell(start, consts.HUS, {}, True)
        if success != consts.HORCM_START_SUCCESSFULLY and success != consts.HORCM_START_ALREADY:
            LOG.error("{}{}{}".format(start, "启动失败", success))
            raise exception.InvalidResults("{}{}{}".format(start, "启动失败", success))

        # 拼接命令
        navi_password = cryptor.decode(self.navi_password)
        cli = consts.LOGIN.format(self.navi_username, navi_password, consts.IH_CLI, self.IH)
        result = NaviClient.execShell(cli, consts.HUS, {}, True)
        # 分析返回结果 什么都没返回说明登录成功
        if result is not None and result != '':
            LOG.error("登录失败：%s" % result)
            raise exception.InvalidResults("登录失败：%s" % result)
        loginToken = 1
        return loginToken

    def getHorCmShutdown(self):
        shotDown = None
        if 'windows' == platform.system().lower():
            shotDown = self.cli(consts.WINDOWS_HORCM_SHUTDOWN.format(self.IH))
        elif 'linux' == platform.system().lower():
            shotDown = self.cli(consts.LINUX_HORCM_SHUTDOWN.format(self.IH))
        if consts.HORCM_SHUTDOWN != shotDown:
            LOG.error("退出进程失败：%s" % shotDown)

    def cli(self, cli):
        returnValue = None
        try:
            returnValue = NaviClient.execShell(cli, consts.HUS, {}, True)
        except Exception as e:
            LOG.error("Get %s error: %s", (cli, six.text_type(e)))
        return returnValue

    # raidqry -l -IH0
    def getRaidQry(self, storage_map):
        raidQryStr = self.cli(consts.RAIDQRY.format(consts.IH_CLI, self.IH))
        if raidQryStr is None or raidQryStr == '':
            return storage_map
        LOG.info("raidQryStr:%s" % raidQryStr)
        raidQryArr = raidQryStr.split('\n')
        LOG.info("raidQryArr:%s" % (json.dumps(raidQryArr, ensure_ascii=False)))
        if len(raidQryArr) < 1:
            return storage_map
        raidQryKey = raidQryArr[0].split()
        for i in range(1, len(raidQryArr)):
            raidQryValue = raidQryArr[i].split()
            storage_map['serial_number'] = raidQryValue[raidQryKey.index('Serial#')]
            storage_map['firmware_version'] = raidQryValue[raidQryKey.index('Micro_ver')]
        LOG.info("raidQryStr封装的值:%s" % (json.dumps(storage_map, ensure_ascii=False)))
        return storage_map

    # raidcom get parity_grp -IH0
    def getParityGrp(self):
        storage_map = dict()
        cli = consts.PARITY_GRP.format(consts.IH_CLI, self.IH)
        storageStr = self.cli(cli)
        if storageStr is None or storageStr == '':
            return storage_map
        LOG.info("getParityGrp_cli:%s" % storageStr)
        storageArr = storageStr.split('\n')
        LOG.info("storageArr:%s" % (json.dumps(storageArr, ensure_ascii=False)))
        if len(storageArr) < 1:
            return storage_map
        storage_key = storageArr[0].split()
        for i in range(1, len(storageArr)):
            storage_value = storageArr[i].split()
            group = storage_value[storage_key.index('GROUP')]
            storage_map['name'] = consts.VENDER.format(group)

            # DRIVE_Capa累加起来就是 raw_capacity
            free_capacity = int(storage_value[storage_key.index('AV_CAP(GB)')])
            storage_map['free_capacity'] = 1024 * 1024 * 1024 * free_capacity

            makeUp = int(storage_value[storage_key.index('U(%)')])
            makeUpNumber = round(1 - makeUp / 100, 2)
            total_capacity = int(free_capacity / makeUpNumber)
            storage_map['total_capacity'] = 1024 * 1024 * 1024 * total_capacity
            storage_map['raw_capacity'] = 1024 * 1024 * 1024 * total_capacity
            # used_capacity = total_capacity - int(free_capacity)
            # storage_map['used_capacity'] = 1024 * 1024 * 1024 * used_capacity

            storage_map['vendor'] = consts.HUS_VM
            storage_map['model'] = consts.HUS_VM
            storage_map['description'] = ""
            storage_map['location'] = ""
        LOG.info("parity_grp封装的值：%s" % (json.dumps(storage_map, ensure_ascii=False)))
        return storage_map

    def getParityGrpID(self, storage_map):
        name = storage_map.get('name')[6:]
        cli = consts.PARITY_GRP_ID.format(name, consts.IH_CLI, self.IH)
        parityGrpId = self.cli(cli)
        if parityGrpId is None or parityGrpId == '':
            return storage_map
        LOG.info("getParityGrpID_cli:%s" % parityGrpId)
        parityGrpIdArr = parityGrpId.split('\n')
        LOG.info("parityGrpIdArr:%s" % (json.dumps(parityGrpIdArr, ensure_ascii=False)))
        if len(parityGrpIdArr) < 1:
            return storage_map
        parityGrpId_key = parityGrpIdArr[0].split()
        for i in range(1, len(parityGrpIdArr)):
            parityGrpId_value = parityGrpIdArr[i].split()
            sts = parityGrpId_value[parityGrpId_key.index('STS')]
            if sts == 'NML':
                storage_map['status'] = constants.StorageStatus.NORMAL
            elif sts == 'REG':
                storage_map['status'] = constants.StorageStatus.OFFLINE
                break
            elif sts == 'DEL':
                storage_map['status'] = constants.StorageStatus.ALL
                break
        return storage_map

    # 根据name执行 raidcom get ldev -ldev_list parity_grp -parity_grp_id 1-1 -IH0拿到DRIVE_Capa
    def getVolumeList(self, storage_map, poolList):
        used_capacity = 0
        for i in poolList:
            poolUsedCapacity = i['used_capacity']
            used_capacity += poolUsedCapacity
        storage_map['used_capacity'] = used_capacity
        return storage_map



