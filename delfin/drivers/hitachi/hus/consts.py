# Copyright 2020 The SODA Authors.
# Copyright (c) 2016 Huawei Technologies Co., Ltd.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# 返回cli命令提示符号
# horcmstart.exe 启动命令启动失败
HORCM_START_FAILED = 'starting HORCM\nHORCM has failed to start.'
# horcmstart.exe 启动命令启动成功
HORCM_START_SUCCESSFULLY = 'starting HORCM inst 0\nHORCM inst 0 starts successfully.'
# horcmstart.exe 启动命令已经启动成功了
HORCM_START_ALREADY = 'HORCM inst 0 has already been running.'
# horcmshutdown.sh 0 返回正常关闭的命令
HORCM_SHUTDOWN = 'inst 0:\nHORCM Shutdown inst 0 !!!'

# 常量
VENDER = 'HUS VM{}'
HUS_VM = 'HUS VM'

# cli命令的拼接
# login
LOGIN = 'raidcom -login {} {} {}{}'
# raidcom get pool -key opt
POOL_KEY_OPT = 'raidcom get pool -key opt {}{}'
# raidcom get pool
RAID_COM_POOL = 'raidcom get pool {}{}'
# raidcom get pool -key basic -IH0
RAID_COM_POOL_KEY_BASIC = 'raidcom get pool -key basic {}{}'
# raidcom get parity_grp -IH0
PARITY_GRP = 'raidcom get parity_grp {}{}'
# raidcom get parity_grp -parity_grp_id 需要拼接参数
PARITY_GRP_ID = 'raidcom get parity_grp -parity_grp_id {} {}{}'
# raidcom get ldev -ldev_list parity_grp -parity_grp_id
RAID_GET_VOLUMES = 'raidcom get ldev -ldev_list parity_grp -parity_grp_id {} {}{}'
# -IH0
IH_CLI = '-IH'
# raidcom get port -IH0
RAID_GET_PORT = 'raidcom get port {}{}'
HUS = 'hus'
WINDOWS_HORCM_START = 'horcmstart.exe {}'
LINUX_HORCM_START = 'horcmstart.sh {}'
# horcmshutdown.sh 0
WINDOWS_HORCM_SHUTDOWN = 'horcmshutdown.exe {}'
LINUX_HORCM_SHUTDOWN = 'horcmshutdown.sh {}'
# raidcom get host_grp -port CL1-A -IH0
RAID_GET_HOST_GRP = 'raidcom get host_grp -port {} {}{}'
# raidcom get lun -port CL2-A liuch-host-group-app -IH0
RAID_GET_lUN = 'raidcom get lun -port {} {} {}{}'
# raidcom get ldev -ldev_id 514 -IH0
RAID_GET_LDEV = 'raidcom get ldev -ldev_id {} {}{}'
# raidqry -l -IH0
RAIDQRY = 'raidqry -l {}{}'


