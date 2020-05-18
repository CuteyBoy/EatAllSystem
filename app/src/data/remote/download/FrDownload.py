import random
from app.src.utils.TimeUtils import StockTimeUtils
from app.src.data.remote.download.DataTools import AsyncRequest
from app.src.data.database.table.StockTable import StockTable
from app.src.data.database.table.StockFrTable import StockFrTable


class FrDownload(AsyncRequest):

    async def _success_handle(self, url, response):
        pass

    async def _fail_handle(self, url, error_code):
        pass

    @classmethod
    def _pack_params(cls, code, page_size, page_index):
        start_time = StockTimeUtils.get_start_time()
        end_time = StockTimeUtils.get_now_time_str()
        return {
            "seDate": [start_time if start_time else "", end_time if end_time else ""],
            "stock": [code if code else "000001"],
            "channelCode": ["fixed_disc"],
            "bigCategoryId": ["010301"],
            "pageSize": page_size,
            "pageNum": page_index if page_index else 1
        }

    @classmethod
    def _headers(cls):
        return {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/80.0.3987.163 Safari/537.36",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Origin": "http://www.szse.cn",
            "Referer": "http://www.szse.cn/disclosure/listed/fixed/index.html?name=%E5%B9%B3%E5%AE%89%E9%93%B6%E8%A1"
                       "%8C&stock=000001&r=1587287453145",
            "Cookie": "CASTGC=TGT-477-dIxsAc1g1gRKtYb3G2ioR2tOWxB2tw9PfxZpMlGCmHnujZxVGi-cas01.example.org; "
                      "JSESSIONID=719b57a5-9054-4912-b070-626d18709c1e",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-Request-Type": "ajax"
        }

    @classmethod
    def _get_url(cls):
        return "http://www.szse.cn/api/disc/announcement/annList?random=%s" % random.random()

    def download_to_db(self):
        url = self._get_url()
        headers = self._headers()
        params = self._pack_params("", 20, 0)
