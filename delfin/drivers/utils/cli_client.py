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
from subprocess import Popen, PIPE
from delfin import exception
from oslo_log import log as logging
import six

LOG = logging.getLogger(__name__)


class NaviClient(object):

    @staticmethod
    def exec(command_str, storage_model, exception_map, stdin_value=None):
        try:
            p = Popen(command_str, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                      shell=False)
        except FileNotFoundError as e:
            err_msg = storage_model + \
                " cli tool not found: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.ComponentNotFound(storage_model + " cli" + e)
        except Exception as e:
            err_msg = storage_model + \
                " cli exec error: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

        if stdin_value:
            out, err = p.communicate(
                input=bytes(stdin_value, encoding='utf-8'))
        else:
            out = p.stdout.read()
        if isinstance(out, bytes):
            out = out.decode("utf-8")
        result = out.strip()
        if result:
            # Determine whether an exception occurs according
            # to the returned information
            for exception_key in exception_map.keys():
                if exception_key in result:
                    LOG.error(storage_model + ' exec failed: %s' % result)
                    raise exception_map.get(exception_key)(result)

        return result

    @staticmethod
    def execShell(command_str, storage_model, exception_map, shell, stdin_value=None):
        try:
            p = Popen(command_str, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                      shell=shell)
        except FileNotFoundError as e:
            err_msg = storage_model + \
                      " cli tool not found: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.ComponentNotFound(storage_model + " cli" + e)
        except Exception as e:
            err_msg = storage_model + \
                      " cli exec error: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

        if stdin_value:
            out, err = p.communicate(
                input=bytes(stdin_value, encoding='utf-8'))
        else:
            out = p.stdout.read()
        if isinstance(out, bytes):
            out = out.decode("utf-8")
        result = out.strip()
        if result:
            # Determine whether an exception occurs according
            # to the returned information
            for exception_key in exception_map.keys():
                if exception_key in result:
                    LOG.error(storage_model + ' exec failed: %s' % result)
                    raise exception_map.get(exception_key)(result)
        return result
