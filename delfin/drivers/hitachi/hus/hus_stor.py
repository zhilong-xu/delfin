import json

from oslo_log import log

from delfin.common import constants
from delfin.drivers.hitachi.hus import ssh_handler, consts
from delfin.drivers import driver

LOG = log.getLogger(__name__)


# hus
class HitachiHusDriver(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ssh_handler = ssh_handler.SSHHandler(**kwargs)
        self.login = self.ssh_handler.login()

    def list_volumes(self, context):
        nativeVolumeId = []
        # basic卷
        volumes = self.getBasicVolume(nativeVolumeId)
        # 逻辑卷
        self.getDbVolume(nativeVolumeId, volumes)
        LOG.info("list_volumes返回的值：%s" % (json.dumps(volumes, ensure_ascii=False)))
        # self.ssh_handler.getHorCmShutdown()
        return volumes

    def add_trap_config(self, context, trap_config):
        pass

    def clear_alert(self, context, alert):
        pass

    # 系统
    def get_storage(self, context):
        # raidcom get parity_grp -IH0
        storage_map = self.ssh_handler.getParityGrp()
        storage_map = self.ssh_handler.getParityGrpID(storage_map)
        # raidqry -l -IH0
        storage_map = self.ssh_handler.getRaidQry(storage_map)
        # 根据name执行 raidcom get ldev -ldev_list parity_grp -parity_grp_id 1-1 -IH0拿到DRIVE_Capa
        poolList = self.getPoolKeyBasic()
        LOG.info("poolList返回的值：%s" % (json.dumps(poolList, ensure_ascii=False)))
        storage_map = self.ssh_handler.getVolumeList(storage_map, poolList)
        LOG.info("get_storage返回的值：%s" % (json.dumps(storage_map, ensure_ascii=False)))
        return storage_map

    def list_alerts(self, context, query_para=None):
        pass

    def list_controllers(self, context):
        pass

    def list_disks(self, context):
        pass

    def list_ports(self, context):
        port_list = []
        portStr = self.ssh_handler.cli(consts.RAID_GET_PORT.format(consts.IH_CLI, self.ssh_handler.IH))
        if portStr is not None and portStr != '':
            portArr = portStr.split('\n')
            if len(portArr) > 1:
                port_key = portArr[0].split()
                for i in range(1, len(portArr)):
                    port_value = portArr[i].split()
                    port_dict = dict()
                    # port_dict['status'] = port_value[port_key.index('STS')]
                    port_dict['native_port_id'] = port_value[port_key.index('PORT')]
                    portType = port_value[port_key.index('TYPE')]
                    if 'FIBRE' == portType:
                        port_dict['type'] = constants.PortType.FC
                    elif 'ISCSI' == portType:
                        port_dict['type'] = constants.PortType.ISCSI
                    elif 'FICON' == portType:
                        port_dict['type'] = constants.PortType.FICON
                    elif 'FCoE' == portType:
                        port_dict['type'] = constants.PortType.FCOE
                    else:
                        port_dict['type'] = constants.PortType.FC
                    port_dict['wwn'] = port_value[port_key.index('WWN')]
                    port_dict['storage_id'] = port_value[port_key.index('Serial#')]
                    port_list.append(port_dict)
        LOG.info("list_ports返回的值：%s" % (json.dumps(port_list, ensure_ascii=False)))
        # self.ssh_handler.getHorCmShutdown()
        return port_list

    # 池
    def list_storage_pools(self, context):
        poolList = self.getPoolKeyBasic()
        LOG.info("list_storage_pools返回的值：%s" % (json.dumps(poolList, ensure_ascii=False)))
        return poolList

    def remove_trap_config(self, context, trap_config):
        pass

    def reset_connection(self, context, **kwargs):
        pass

    def list_quotas(self, context):
        pass

    def list_filesystems(self, context):
        pass

    def list_qtrees(self, context):
        pass

    def list_shares(self, context):
        pass

    def getPoolKeyBasic(self):
        poolList = []
        poolStr = self.ssh_handler.cli(consts.RAID_COM_POOL_KEY_BASIC.format(consts.IH_CLI, self.ssh_handler.IH))
        LOG.info("poolStr:%s" % (json.dumps(poolStr, ensure_ascii=False)))
        # 筛选数据
        if poolStr is not None and poolStr != '':
            pool_arr = poolStr.split('\n')
            LOG.info("poolStr_arr:%s" % (json.dumps(pool_arr, ensure_ascii=False)))
            # 有数据才去找
            if len(pool_arr) > 1:
                # 先拿到key
                arr_keyMap = pool_arr[0].split()
                # 第一层分割每行，包含了key
                for i in range(1, len(pool_arr)):
                    system = dict()
                    # value 值
                    arr_value = pool_arr[i].split()
                    system['name'] = arr_value[arr_keyMap.index('POOL_NAME')]
                    system['description'] = 'Hitachi hus Pool'
                    status = arr_value[arr_keyMap.index('POLS')]
                    if status == 'POLN':
                        system['status'] = constants.StoragePoolStatus.NORMAL
                    elif status == 'POLF' or status == 'POLS':
                        system['status'] = constants.StoragePoolStatus.OFFLINE
                    elif status == ' POLE':
                        system['status'] = constants.StoragePoolStatus.ABNORMAL
                    if "OPEN" == arr_value[arr_keyMap.index('TYPE')]:
                        system['storage_type'] = constants.StorageType.BLOCK
                    else:
                        system['storage_type'] = constants.StorageType.FILE
                    PID = arr_value[arr_keyMap.index('PID')]
                    system['native_storage_pool_id'] = PID
                    system['storage_id'] = self.storage_id
                    total_capacity = int(arr_value[arr_keyMap.index('Capacity(MB)')]) * 1024 ** 2
                    system['total_capacity'] = total_capacity
                    used_capacity = int(arr_value[arr_keyMap.index('TL_CAP(MB)')]) * 1024 ** 2
                    system['used_capacity'] = used_capacity
                    system['free_capacity'] = total_capacity - used_capacity
                    poolList.append(system)
        return poolList

    # basic卷获取
    def getBasicVolume(self, nativeVolumeId):
        storage_map = self.ssh_handler.getParityGrp()
        group = storage_map.get('name')
        LOG.info("getBasicVolume__group:%s" % group)
        # if name is not None and name != '':
        if group is None or group == '':
            return
        group = group[6:]
        # 拿到 GROUP 之后把参数传入
        cli = consts.RAID_GET_VOLUMES.format(group, consts.IH_CLI, self.ssh_handler.IH)
        volumeStr = self.ssh_handler.cli(cli)
        LOG.info("getBasicVolume__volumeStr:%s" % volumeStr)
        # if volumeStr is not None and volumeStr != '':
        if volumeStr is None or volumeStr == '':
            return
        # 拿到每一组数据
        volumeArr = volumeStr.split('\n\n')
        LOG.info("getBasicVolume__volumeArr:%s" % (json.dumps(volumeArr, ensure_ascii=False)))
        if len(volumeArr) < 1:
            return
        volumes = []
        for i in range(0, len(volumeArr)):
            tab = False
            # 每一组数据再分割成每一行
            keyValueArr = volumeArr[i].split('\n')
            volume_dict = dict()
            tab = self.getRowData(keyValueArr, nativeVolumeId, tab, volume_dict)
            if tab:
                continue
            volume_dict['description'] = 'Hitachi HUS volume'
            volume_dict['compressed'] = True
            volume_dict['deduplicated'] = True
            volumes.append(volume_dict)
        LOG.info("getBasicVolume__volumes:%s" % (json.dumps(volumes, ensure_ascii=False)))
        return volumes

    def getRowData(self, keyValueArr, nativeVolumeId, tab, volume_dict):
        total_capacity = 0
        used_capacity = 2147483648
        for j in range(0, len(keyValueArr)):
            arr = keyValueArr[j].split(':')
            key = arr[0].strip()
            value = arr[1].strip()
            if key == 'STS':
                if value == 'NML':
                    volume_dict['status'] = constants.StorageStatus.NORMAL
                else:
                    volume_dict['status'] = constants.StorageStatus.ABNORMAL
            elif key == 'VOL_TYPE':
                if 'OPEN-V-CVS' == value:
                    volume_dict['type'] = constants.VolumeType.THIN
                else:
                    volume_dict['type'] = constants.VolumeType.THICK
            elif key == 'LDEV':
                # 如果包含就把tab改成true
                if value in nativeVolumeId:
                    tab = True
                    break
                volume_dict['native_volume_id'] = value
                nativeVolumeId.append(value)
            elif key == 'F_POOLID':
                if 'NONE' != value:
                    volume_dict['native_storage_pool_id'] = value
            elif key == 'B_POOLID':
                volume_dict['native_storage_pool_id'] = value
            elif key == 'LDEV_NAMING':
                if '' == value or None is value:
                    value = '未知'
                volume_dict['name'] = value
            elif key == 'Serial#':
                volume_dict['storage_id'] = self.storage_id
            elif key == 'VOL_Capacity(BLK)':
                total_capacity = int(value) * 512
                volume_dict['total_capacity'] = total_capacity
            elif key == 'Used_Block(BLK)':
                used_capacity = int(value) * 512
        volume_dict['used_capacity'] = used_capacity
        volume_dict['free_capacity'] = total_capacity - used_capacity
        return tab

    # 逻辑卷
    def getDbVolume(self, nativeVolumeId, volumes):
        # 1 raidcom get port -IH0 拿端口号
        portStr = self.ssh_handler.cli(consts.RAID_GET_PORT.format(consts.IH_CLI, self.ssh_handler.IH))
        LOG.info("getDbVolume_portStr:%s" % portStr)
        if portStr is None or portStr == '':
            return
        portArr = portStr.split('\n')
        LOG.info("getDbVolume_portArr:%s" % (json.dumps(portArr, ensure_ascii=False)))
        if len(portArr) < 1:
            return
        port_key = portArr[0].split()
        for i in range(1, len(portArr)):
            port_value = portArr[i].split()
            port = port_value[port_key.index('PORT')]
            # 2 根据端口号执行raidcom get host_grp -port CL1-A -IH0拿 GROUP_NAME
            self.getHostGrp(nativeVolumeId, port, volumes)

    # 2 根据端口号执行raidcom get host_grp -port CL1-A -IH0拿 GROUP_NAME
    def getHostGrp(self, nativeVolumeId, port, volumes):
        hostGrpCli = consts.RAID_GET_HOST_GRP.format(port, consts.IH_CLI, self.ssh_handler.IH)
        groupNameStr = self.ssh_handler.cli(hostGrpCli)
        LOG.info("getHostGrp_groupNameStr:%s" % groupNameStr)
        if groupNameStr is None or groupNameStr == '':
            return
        groupNameArr = groupNameStr.split('\n')
        LOG.info("getHostGrp_groupNameArr:%s" % (json.dumps(groupNameArr, ensure_ascii=False)))
        if len(groupNameArr) < 1:
            return
        groupNameKey = groupNameArr[0].split()
        for j in range(1, len(groupNameArr)):
            groupNameValue = groupNameArr[j].split()
            # 拿到GROUP_NAME
            groupName = groupNameValue[groupNameKey.index('GROUP_NAME')]
            # 根据端口号和 GROUP_NAME 执行 raidcom get lun -port CL2-A liuch-host-group-app -IH0 拿到 LDEV
            lunCli = consts.RAID_GET_lUN.format(port, groupName, consts.IH_CLI, self.ssh_handler.IH)
            lunStr = self.ssh_handler.cli(lunCli)
            LOG.info("getHostGrp_lunCli:%s" % lunCli)
            LOG.info("getHostGrp_lunStr:%s" % lunStr)
            if lunStr is None or lunStr == '':
                return
            lunArr = lunStr.split('\n')
            LOG.info("getHostGrp_lunArr:%s" % (json.dumps(lunArr, ensure_ascii=False)))
            if len(lunArr) < 1:
                return
            lunKey = lunArr[0].split()
            for k in range(1, len(lunArr)):
                lunValue = lunArr[k].split()
                ldev = lunValue[lunKey.index('LDEV')]
                if ldev in nativeVolumeId:
                    continue
                nativeVolumeId.append(ldev)
                self.getLdev(ldev, volumes)

    # 根据拿到的LDEV 带入raidcom get ldev -ldev_id 514 -IH0
    def getLdev(self, ldev, volumes):
        cli = consts.RAID_GET_LDEV.format(ldev, consts.IH_CLI, self.ssh_handler.IH)
        ldevStr = self.ssh_handler.cli(cli)
        LOG.info("getLdev_ldevStr:%s" % (json.dumps(ldevStr, ensure_ascii=False)))
        if ldevStr is None or ldevStr == '':
            return
        ldevArr = ldevStr.split('\n')
        LOG.info("getLdev_ldevArr:%s" % (json.dumps(ldevArr, ensure_ascii=False)))
        dp_dict = dict()
        total_capacity = 0
        used_capacity = 0
        for p in range(0, len(ldevArr)):
            arr = ldevArr[p].split(':')
            key = arr[0].strip()
            value = arr[1].strip()
            if key == 'STS':
                if value == 'NML':
                    dp_dict['status'] = constants.StorageStatus.NORMAL
                else:
                    dp_dict['status'] = constants.StorageStatus.ABNORMAL
            elif key == 'VOL_TYPE':
                if 'OPEN-V-CVS' == value:
                    dp_dict['type'] = constants.VolumeType.THIN
                else:
                    dp_dict['type'] = constants.VolumeType.THICK
            elif key == 'LDEV':
                dp_dict['native_volume_id'] = value
            elif key == 'F_POOLID':
                if 'NONE' != value:
                    dp_dict['native_storage_pool_id'] = value
            elif key == 'B_POOLID':
                dp_dict['native_storage_pool_id'] = value
            elif key == 'LDEV_NAMING':
                if '' == value or None is value:
                    value = '未知'
                dp_dict['name'] = value
            elif key == 'VOL_Capacity(BLK)':
                total_capacity = int(value) * 512
                dp_dict['total_capacity'] = total_capacity
            elif key == 'Used_Block(BLK)':
                used_capacity = int(value) * 512
        dp_dict['used_capacity'] = used_capacity
        dp_dict['free_capacity'] = total_capacity - used_capacity
        dp_dict['description'] = 'Hitachi HUS volume'
        dp_dict['compressed'] = True
        dp_dict['deduplicated'] = True
        dp_dict['storage_id'] = self.storage_id
        LOG.info("getLdev封装的对象:%s" % (json.dumps(dp_dict, ensure_ascii=False)))
        volumes.append(dp_dict)
