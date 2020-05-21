import random
import aiohttp
from app.src.utils.TimeUtils import StockTimeUtils
from app.src.data.remote.download.DataTools import AsyncTask


class AsyncFrDownload(AsyncTask):

    def __init__(self):
        self.pageSize = 30
        self.pdf_path_key = "attachPath"
        self.title_key = "title"
        self.pdf_size_key = "attachSize"
        self.data_size_key = "announceCount"
        # 010301 年报 010307 三季度报 010303半年报 010305一季度报
        self.bigCategoryId = ["010301", "010307", "010303", "010305"]

    @classmethod
    def _get_url(cls):
        return "http://www.szse.cn/api/disc/announcement/annList?random=%s" % random.random()

    @classmethod
    def _get_headers(cls):
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

    def _get_params(self, code, start_time, page_size, page_index):
        # 如果没有传开始时间
        if start_time is None:
            # 则取结束时间的差5年的时间
            start_time = StockTimeUtils.get_start_time()
        end_time = StockTimeUtils.get_now_time_str()
        return {
            "seDate": [start_time if start_time else "", end_time if end_time else ""],
            "stock": [code if code else "000001"],
            "channelCode": ["fixed_disc"],
            "bigCategoryId": self.bigCategoryId[0],
            "pageSize": page_size,
            "pageNum": page_index if page_index else 1
        }

    async def task(self, data, **kwargs):
        pass

    def start_download(self):
        from app.src.data.database.table.StockTable import StockTable
        stock_table = StockTable()
        stock_list = stock_table.find(filter={}, projection={
            "_id": 0,
            "stock_code": "0",
            "market_time": "0"
        })
        self.run_tasks(stock_list)
