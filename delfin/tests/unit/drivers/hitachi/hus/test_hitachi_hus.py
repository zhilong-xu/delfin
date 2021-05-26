import sys
from unittest import mock, TestCase

from delfin import context

sys.modules['delfin.cryptor'] = mock.Mock()
from delfin.drivers.hitachi.hus.ssh_handler import SSHHandler
from delfin.drivers.hitachi.hus.hus_stor import HitachiHusDriver
from delfin.exception import InvalidResults

ACCESS_INFO = {
    "rest": {
        "host": "127.0.0.1",
        "port": 34001,
        "username": "maintenance",
        "password": "raid-mainte",
        "IH": "0"
    }
}
ACCESS_INFO_HORCM_START_FAILED = {
    "rest": {
        "host": "127.0.0.1",
        "port": 34001,
        "username": "maintenance",
        "password": "raid-mainte",
        "IH": ""
    }
}
POOL_RETURN_VALUE = [
    {'name': 'liuch-pool3', 'native_storage_pool_id': '000', 'status': 'POLN', 'storage_type': 'OPEN',
     'storage_id': '000', 'total_capacity': 36708, 'used_capacity': 36708, 'free_capacity': 0},
    {'name': 'liuchdppool2', 'native_storage_pool_id': '102', 'status': 'POLN', 'storage_type': 'OPEN',
     'storage_id': '102', 'total_capacity': 57204, 'used_capacity': 57204, 'free_capacity': 0},
    {'name': 'liuchdppool22', 'native_storage_pool_id': '103', 'status': 'POLN', 'storage_type': 'OPEN',
     'storage_id': '103', 'total_capacity': 77700, 'used_capacity': 77700, 'free_capacity': 0}
]
volumes = [
    {'status': 'NML', 'native_volume_id': '0', 'type': 'R', 'storage_id': '12345'},
    {'status': 'NML', 'native_volume_id': '1', 'type': 'R', 'storage_id': '12345'},
    {'status': 'NML', 'native_volume_id': '2', 'type': 'R', 'storage_id': '12345'},
    {'status': 'NML', 'native_volume_id': '3', 'type': 'R', 'storage_id': '12345'},
    {'status': 'NML', 'native_volume_id': '257', 'type': 'R', 'storage_id': '12345'},
    {'status': 'NML', 'native_volume_id': '258', 'type': 'R', 'storage_id': '12345'},
    {'status': 'NML', 'native_volume_id': '11', 'type': 'R', 'storage_id': '12345'},
    {'status': 'NML', 'native_volume_id': '12', 'type': 'R', 'storage_id': '12345'},
    {'status': 'NML', 'native_volume_id': '-', 'type': 'R', 'storage_id': '12345'}
]

GET_STORAGE_PARITYGRP = """T GROUP  Num_LDEV  U(%)  AV_CAP(GB) R_LVL  R_TYPE     SL  CL  DRIVE_TYPE         M E_TYPE
                        R   1-1           10    27         873 RAID1  2D+2D       0   0  DKS5G-J600SS       - OPEN-V"""

RAID_QRYSTR = """No Group    Hostname            HORCM_ver  Uid  Serial#    Micro_ver Cache(MB)
                 1  ---     PC-202104101608    01-61-03/01    0   211987  73-03-58/00    121856"""

VOLUME_STR = """Serial#  : 211987
                LDEV : 0
                SL : 0
                CL : 0
                VOL_TYPE : OPEN-V-CVS
                VOL_Capacity(BLK) : 20972160
                NUM_LDEV : 1
                LDEVs : 0
                NUM_PORT : 2
                PORTs : CL3-A-0 0 3A-G00-liuch : CL2-A-0 0 2A-G00
                F_POOLID : NONE
                VOL_ATTR : CVS
                CMP : -
                EXP_SPACE : -
                RAID_LEVEL  : RAID1
                RAID_TYPE   : 2D+2D
                NUM_GROUP : 1
                RAID_GROUPs : 01-01
                DRIVE_TYPE  : DKS5G-J600SS
                DRIVE_Capa : 1143358736
                LDEV_NAMING : liuch-ldev2
                STS : NML
                OPE_TYPE : NONE
                OPE_RATE : 100
                MP# : 0
                SSID : 0004
                ALUA : Disable
                RSGID : 0
                PWSV_S : -
                
                Serial#  : 211987
                LDEV : 1
                SL : 0
                CL : 0
                VOL_TYPE : OPEN-V-CVS
                VOL_Capacity(BLK) : 20972160
                NUM_LDEV : 1
                LDEVs : 1
                NUM_PORT : 0
                PORTs :
                F_POOLID : NONE
                VOL_ATTR : CVS
                CMP : -
                EXP_SPACE : -
                RAID_LEVEL  : RAID1
                RAID_TYPE   : 2D+2D
                NUM_GROUP : 1
                RAID_GROUPs : 01-01
                DRIVE_TYPE  : DKS5G-J600SS
                DRIVE_Capa : 1143358736
                LDEV_NAMING : liuch-ldev3
                STS : NML
                OPE_TYPE : NONE
                OPE_RATE : 100
                MP# : 0
                SSID : 0004
                ALUA : Disable
                RSGID : 0
                PWSV_S : -"""

RAID_COM_POOL_STR = """PID  POLS U(%) SSCNT Available(MB) Capacity(MB)     Seq# Num LDEV# H(%)   FMT_CAP(MB)
                        000  POLN   0      3        36708        36708    211987   2    11  80             -
                        102  POLN   0      5        57204        57204    211987   2     2  80             -
                        103  POLN   0      4        77700        77700    211987   2   257  80             -"""

POOL_KEY_OPT = """PID  POLS U(%) POOL_NAME                            Seq# Num LDEV# H(%) VCAP(%) TYPE PM PT  AUTO_ADD_PLV
                   000  POLN   0  liuch-pool3                        211987   2    11  80       -  OPEN N  HDP -
                   102  POLN   0  liuchdppool2                       211987   2     2  80      10  OPEN N  HDP -
                   103  POLN   0  liuchdppool22                      211987   2   257  80      20  OPEN N  HDP -"""

RAID_GET_PORT = """PORT   TYPE  ATTR   SPD  LPID  FAB  CONN  SSW   SL   Serial#  WWN               PHY_PORT
                CL1-A  FIBRE TAR    AUT    EF  N    FCAL  N      0    211987  50060e80132ed300  -
                CL2-A  FIBRE TAR    AUT    D9  N    FCAL  N      0    211987  50060e80132ed310  -
                CL3-A  FIBRE TAR    AUT    E8  N    FCAL  N      0    211987  50060e80132ed320  -
                CL4-A  FIBRE TAR    AUT    D6  N    FCAL  N      0    211987  50060e80132ed330  -
                CL5-A  FIBRE TAR    AUT    E4  N    FCAL  N      0    211987  50060e80132ed340  -
                CL6-A  FIBRE TAR    AUT    D5  N    FCAL  N      0    211987  50060e80132ed350  -
                CL7-A  FIBRE TAR    AUT    E2  N    FCAL  N      0    211987  50060e80132ed360  -
                CL8-A  FIBRE TAR    AUT    D4  N    FCAL  N      0    211987  50060e80132ed370  -"""

PARITY_GRP = """T GROUP  Num_LDEV  U(%)  AV_CAP(GB) R_LVL  R_TYPE     SL  CL  DRIVE_TYPE         M E_TYPE
                R 1-1           8    18         873 RAID1  2D+2D       0   0  DKS5G-J600SS       - OPEN-V"""

PARITY_GRP_ID = """T GROUP  P_NO  LDEV#   STS         LOC_LBA        SIZE_LBA            Serial# SP
R 1-1       0      0   NML  0x000000000000  0x000001400280             211987 R
R 1-1       1      1   NML  0x000001400800  0x000001400280             211987 R
R 1-1       2      2   NML  0x000002801000  0x000003c00000             211987 R
R 1-1       3      3   NML  0x000006401000  0x000003c00000             211987 R
R 1-1       4    257   NML  0x00000a001000  0x000005000280             211987 R
R 1-1       5    258   NML  0x00000f001800  0x000005000280             211987 R
R 1-1       6     11   NML  0x000014002000  0x000002800500             211987 R
R 1-1       7     12   NML  0x000016802800  0x000002800500             211987 R
R 1-1       8     13   NML  0x000019003000  0x000006400500             211987 R
R 1-1       9     14   NML  0x00001f403800  0x000006400500             211987 R
R 1-1      10      -   NML  0x000025804000  0x000060b37800             211987 -"""

RAID_COM_POOL_KEY_BASIC = """PID  POLS U(%)  LCNT SSCNT Available(MB) Capacity(MB) Snap_Used(MB) TL_CAP(MB) BM  TR_CAP(MB)  RCNT   Seq# Num LDEV# W(%) H(%) STIP    VCAP(%) TYPE PM PT  POOL_NAME
000  POLN   0      3     -         36708        36708             -       9216 -            -     - 211987   2    11   70   80 -     UNLIMITED OPEN N  HDP liuch-pool3
102  POLN   0      5     -         57204        57204             -       3588 -            -     - 211987   2     2   70   80 -            10 OPEN N  HDP liuchdppool2
103  POLN   0      4     -         77700        77700             -       8194 -            -     - 211987   2   257   70   80 -            20 OPEN N  HDP liuchdppool22"""

RETURN_POOL = [
    {'name': 'liuch-pool3', 'description': 'Hitachi hus Pool', 'status': 'normal', 'storage_type': 'block', 'native_storage_pool_id': '000', 'storage_id': None, 'total_capacity': 38491127808, 'used_capacity': 9663676416, 'free_capacity': 28827451392},
    {'name': 'liuchdppool2', 'description': 'Hitachi hus Pool', 'status': 'normal', 'storage_type': 'block', 'native_storage_pool_id': '102', 'storage_id': None, 'total_capacity': 59982741504, 'used_capacity': 3762290688, 'free_capacity': 56220450816},
    {'name': 'liuchdppool22', 'description': 'Hitachi hus Pool', 'status': 'normal', 'storage_type': 'block', 'native_storage_pool_id': '103', 'storage_id': None, 'total_capacity': 81474355200, 'used_capacity': 8592031744, 'free_capacity': 72882323456}
]

def create_driver():
    SSHHandler.login = mock.Mock(return_value=1)
    return HitachiHusDriver(**ACCESS_INFO)


class Test_hitachi_hus(TestCase):
    driver = create_driver()

    # 启动成功，登录成功
    def test_init_success(self):
        SSHHandler.login = mock.Mock(return_value=1)
        vnx = HitachiHusDriver(**ACCESS_INFO)
        self.assertEqual(vnx.login, 1)

    # 启动失败，登录失败
    def test_init_failed(self):
        SSHHandler.login = mock.Mock(return_value=None)
        try:
            vnx = HitachiHusDriver(**ACCESS_INFO_HORCM_START_FAILED)
            self.assertEqual(vnx.login, None)
        except InvalidResults as e:
            self.assertTrue(e is not None)

    # storage 成功场景
    def test_get_storage_success(self):
        SSHHandler.cli = mock.Mock(side_effect=[GET_STORAGE_PARITYGRP, PARITY_GRP_ID, RAID_QRYSTR,
                                                RAID_COM_POOL_KEY_BASIC])
        storage = HitachiHusDriver(**ACCESS_INFO).get_storage(context)
        self.assertEqual(storage['name'], 'HUS VM1-1')

    def test_list_storage_pools(self):
        SSHHandler.cli = mock.Mock(return_value=RAID_COM_POOL_KEY_BASIC)
        pool = HitachiHusDriver(**ACCESS_INFO).list_storage_pools(context)
        self.assertListEqual(pool, RETURN_POOL)

    def test_list_volumes(self):
        SSHHandler.cli = mock.Mock(side_effect=[GET_STORAGE_PARITYGRP, VOLUME_STR, RAID_GET_PORT,
                                                RAID_COM_POOL_KEY_BASIC])
        # basic卷
        # SSHHandler.cli = mock.Mock(return_value=PARITY_GRP)
        # storage_map = SSHHandler(**ACCESS_INFO).getParityGrp()
        # SSHHandler.getParityGrp = mock.Mock(return_value=storage_map)
        #
        # SSHHandler.cli = mock.Mock(return_value=volumeStr)
        # nativeVolumeId = []
        # volumes = SSHHandler(**ACCESS_INFO).getBasicVolume(nativeVolumeId)
        # SSHHandler.getBasicVolume = mock.Mock(return_value=volumes)
        #
        # # 逻辑卷
        # SSHHandler.cli = mock.Mock(return_value=RAID_GET_PORT)
        # SSHHandler.getDbVolume = mock.Mock(return_value=None)
        volumes = HitachiHusDriver(**ACCESS_INFO).list_volumes(context)
        return volumes

    def test_list_ports(self):
        SSHHandler.cli = mock.Mock(return_value=RAID_GET_PORT)
        port = HitachiHusDriver(**ACCESS_INFO).list_ports(context)
        return port
