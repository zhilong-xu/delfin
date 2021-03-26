
import threading

import requests
import six
from oslo_log import log as logging

from delfin import cryptor
from delfin import exception
from delfin.drivers.utils.rest_client import RestClient

LOG = logging.getLogger(__name__)

class RestVolume(RestClient):

    # REST_AUTH_URL = '/api/types/loginSessionInfo/instances'
    # REST_STORAGE_URL = '/api/types/system/instances'
    # REST_CAPACITY_URL = '/api/types/systemCapacity/instances'
    # REST_SOFT_VERSION_URL = '/api/types/installedSoftwareVersion/instances'
    REST_VOLUME_URL = '/xiv/v3/volumes'
    # REST_POOLS_URL = '/api/types/pool/instances'
    # REST_ALERTS_URL = '/api/types/alert/instances'
    # REST_DEL_ALERTS_URL = '/api/instances/alert/'
    # REST_LOGOUT_URL = '/api/types/loginSessionInfo/action/logout'
    AUTH_KEY = 'EMC-CSRF-TOKEN'
    STATE_SOLVED = 2

    def __init__(self, **kwargs):
        super(RestVolume, self).__init__(**kwargs)
        self.session_lock = threading.Lock()

    def login(self):
        """Login dell_emc unity storage array."""
        try:
            with self.session_lock:
                data = {}
                if self.session is None:
                    self.init_http_head()
                self.session.headers.update({"X-EMC-REST-CLIENT": "true"})
                self.session.auth = requests.auth.HTTPBasicAuth(
                    self.rest_username, cryptor.decode(self.rest_password))
                res = self.call_with_token(
                    RestVolume.REST_AUTH_URL, data, 'GET')
                if res.status_code == 200:
                    self.session.headers[RestVolume.AUTH_KEY] = \
                        cryptor.encode(res.headers[RestVolume.AUTH_KEY])
                else:
                    LOG.error("Login error.URL: %s,Reason: %s.",
                              RestVolume.REST_AUTH_URL, res.text)
                    if 'Unauthorized' in res.text:
                        raise exception.InvalidUsernameOrPassword()
                    elif 'Forbidden' in res.text:
                        raise exception.InvalidIpOrPort()
                    else:
                        raise exception.BadResponse(res.text)
        except Exception as e:
            LOG.error("Login error: %s", six.text_type(e))
            raise e

    def get_all_rest_volumes(self):
        result_json = self.get_rest_info(RestVolume.REST_VOLUME_URL)
        return result_json

    def get_rest_info(self, url, data=None, method='GET'):
        result_json = None
        # res = self.call(url, data, method)

        # 请求远程接口
        res = self.do_call(self, url, data, method)
        if res.status_code == 200:
            result_json = res.json()
        return result_json

    # 自定义远程调用方法 暂时不用
    def call(self, url, data=None, method=None):
        try:
            res = self.call_with_token(url, data, method)
            if res.status_code == 401:
                LOG.error("Failed to get token, status_code:%s,error_mesg:%s" %
                          (res.status_code, res.text))
                self.login()
                res = self.call_with_token(url, data, method)
            elif res.status_code == 503:
                raise exception.InvalidResults(res.text)
            return res
        except Exception as e:
            LOG.error("Method:%s,url:%s failed: %s" % (method, url,
                                                       six.text_type(e)))
            raise e

    def call_with_token(self, url, data, method):
        auth_key = None
        if self.session:
            auth_key = self.session.headers.get(RestVolume.AUTH_KEY, None)
            if auth_key:
                self.session.headers[RestVolume.AUTH_KEY] \
                    = cryptor.decode(auth_key)
        res = self.do_call(url, data, method)
        if auth_key:
            self.session.headers[RestVolume.AUTH_KEY] = auth_key
        return res