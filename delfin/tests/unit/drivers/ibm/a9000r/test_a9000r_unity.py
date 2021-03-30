# Copyright 2021 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys

from unittest import TestCase, mock

sys.modules['delfin.cryptor'] = mock.Mock()
from delfin import context
from delfin.drivers.ibm.a9000r.rest_volume import RestVolume
from delfin.drivers.ibm.a9000r.unity_volume import UnityVolume
from delfin.drivers.ibm.a9000r.ssh_volume import SSHVolume

ACCESS_INFO = {
    "storage_id": "12345",
    "rest": {
        "host": "110.143.132.231",
        "port": "8443",
        "username": "username",
        "password": "cGFzc3dvcmQ="
    }
}

GET_ALL_VOLUME = {
    "volume": {
        "size_on_disk": "103000000000",
        "pool_ref": "/xiv/v3/:6011947b/pools/:Pool_DM",
        "size": "103249084416",
        "wwn": "001738002EAB3AAB",
        "capacity_used_by_snapshots": "0",
        "id": "6d5d14d03ab5",
        "ref": "/xiv/v3/:6011947b/volumes/:Vol_RTC_004",
        "system": "6011947b",
        "pool": "Pool_DM",
        "name": "Vol_RTC_004",
        "mirrored": "false",
        "cg": "",
        "locked": "false",
        "used_capacity": "12000000000",
        "perf_class_ref": "/xiv/v3/:gen4d-54c/perf_classes/:TaylorS",
        "perf_class": "TaylorS",
        "estimated_min_delete_size": "0"
    }
}
GET_STORAGE = {
    "system": {
        "hard_capacity": "",
        "safe_mode": "false",
        "system_state": "on",
        "soft_capacity": "",
        "compression_state": "",
        "free_soft_capacity": "",
        "ref": "/xiv/v3/systems/:gen4d-64b",
        "target_state": "on",
        "name": "gen4d-64b",
        "physical_free": "1937000000000",
        "redundancy_status": "Fully Protected",
        "id": "XIV gen4d-64b:6013794:9835:415",
        "physical_size": "1963000000000",
        "serial_number": "12",
        "firmware_version": "10.2"
    },
}
SERIAL_NUMBER = "12"
FIRMWARE_VERSION = "10.2"

GET_POOL = {
    "pool": {
        "used_by_snapshots": "0",
        "snapshot_size": "309000000000",
        "size": "23050000000000",
        "id": "6dc714800006",
        "ref": "/xiv/v3/:6011947b/pools/:Clippers",
        "system": "6011947b",
        "used_by_volumes": "860000000000",
        "name": "Clippers",
        "domain": "no-domain",
        "locked": "false",
        "perf_class_ref": "/xiv/v3/:gen4d-54c/perf_classes/:TaylorS",
        "perf_class": "TaylorS"
    }
}


class TestUNITYStorDriver(TestCase):

    @mock.patch.object(RestVolume, 'get_all_rest_volumes')
    def test_list_volumes(self, mock_lun):
        RestVolume.login = mock.Mock(return_value=None)
        mock_lun.side_effect = [GET_ALL_VOLUME]
        volume = UnityVolume(**ACCESS_INFO).list_volumes(context)
        self.assertEqual(volume.get("volume").get("name"), GET_ALL_VOLUME.get("volume").get("name"))
        self.assertEqual(volume.get("volume").get("native_volume_id"), GET_ALL_VOLUME.get("volume").get("id"))
        self.assertEqual(volume.get("volume").get("total_capacity"), GET_ALL_VOLUME.get("volume").get("size"))
        self.assertEqual(volume.get("volume").get("used_capacity"), GET_ALL_VOLUME.get("volume").get("used_capacity"))

    @mock.patch.object(RestVolume, 'get_storage')
    @mock.patch.object(SSHVolume, 'get_storage_serial_number')
    @mock.patch.object(SSHVolume, 'get_storage_version_get')
    def test_get_storage(self, firmware_version, serial_number, get_storage):
        RestVolume.login = mock.Mock(return_value=None)
        # 注意mock先后的顺序
        get_storage.return_value = GET_STORAGE
        serial_number.return_value = SERIAL_NUMBER
        firmware_version.return_value = FIRMWARE_VERSION
        volume = UnityVolume(**ACCESS_INFO).get_storage(context)
        self.assertEqual(volume.get("system").get("name"), GET_STORAGE.get("system").get("name"))
        self.assertEqual(volume.get("system").get("serial_number"), "12")
        self.assertEqual(volume.get("system").get("version_get"), "10.2")

    @mock.patch.object(RestVolume, 'get_all_pools')
    def test_list_storage_pools(self, mock_lun):
        RestVolume.login = mock.Mock(return_value=None)
        mock_lun.side_effect = [GET_POOL]
        volume = UnityVolume(**ACCESS_INFO).list_storage_pools(context)
        self.assertEqual(volume.get("pool").get("name"), GET_POOL.get("pool").get("name"))
        self.assertEqual(volume.get("pool").get("native_storage_pool_id"), GET_POOL.get("pool").get("id"))
        self.assertEqual(volume.get("pool").get("total_capacity"), GET_POOL.get("pool").get("size"))
        self.assertEqual(volume.get("pool").get("used_capacity"), GET_POOL.get("pool").get("used_by_volumes"))
