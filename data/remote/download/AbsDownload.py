import requests
import abc
from log import Log


class AbsDownload(metaclass=abc.ABCMeta):
    """
    封装下载数据的基础类，用来实现各种下载数据并进行保存操作
    """

    def __init__(self, table=None):
        self.table = table
        self.data_key = "data"
        self.d = Log.d

    @abc.abstractmethod
    def _get_url(self, **kwargs):
        """
        用于子类重新返回请求地址
        :return:
        """
        pass

    @abc.abstractmethod
    def _get_headers(self, **kwargs):
        """
        用于子类重写返回请求参数头信息
        :return:
        """
        pass

    @abc.abstractmethod
    def _get_params(self, **kwargs):
        """
        用于子类从写返回请求的参数
        :return:
        """
        pass

    @abc.abstractmethod
    def download_to_db(self, **kwargs):
        """
        用来实现开始下载并保存到数据库的操作
        :return:
        """
        pass

    def get_request_result(self, **kwargs):
        """
        得到请求结果
        :return:
        """
        url = self._get_url(**kwargs)
        headers = self._get_headers(**kwargs)
        params = self._get_params(**kwargs)
        result = requests.get(url, headers=headers, params=params, stream=kwargs.get("stream"))
        if result and result.status_code == 200:
            return result
        else:
            self.d("%s get request error" % url)
            return None

    def post_request_result(self, **kwargs):
        """
        post请求数据
        :param kwargs:
        :return:
        """
        url = self._get_url(**kwargs)
        headers = self._get_headers(**kwargs)
        json_params = self._get_params(**kwargs)
        result = requests.post(url, headers=headers, data=json_params, stream=kwargs.get("stream"))
        if result and result.status_code == 200:
            return result
        else:
            self.d("%s post request error" % url)
            return None