import random
from app.src.data.remote.download.AbsDownload import AbsDownload


class XlsDownload(AbsDownload):
    """
    下载所有的股票Xls格式的并将数据解析存入数据库
    """

    def _get_url(self, **kwargs):
        return """http://www.szse.cn/api/report/ShowReport"""

    def _get_headers(self, **kwargs):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image"
                      "/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/80.0.3987.163 Safari/537.36",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "http://www.szse.cn/market/stock/list/index.html",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": 1
        }

    def _get_params(self, **kwargs):
        return {
            "SHOWTYPE": "xlsx",
            "CATALOGID": "1110",
            "TABKEY": "tab1",
            "random": random.random()
        }

    def download_to_db(self, **kwargs):
        pass
