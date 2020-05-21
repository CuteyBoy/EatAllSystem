import random
import aiohttp
import math
from app.src.data.database.table.StockFrTable import StockFrTable
from app.src.utils.TimeUtils import StockTimeUtils
from app.src.data.remote.download.DataTools import AsyncTask

# pdf下载基础地址
DPF_DOWNLOAD_BASE_URL = "http://disc.static.szse.cn/download"


class AsyncFrDownload(AsyncTask):

    def __init__(self):
        self.table = StockFrTable()
        self.pageSize = 30
        self.data_key = "data"
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

    async def package_tasks(self, data_list, **kwargs):
        async with aiohttp.ClientSession(cookies=kwargs.get("cookies")) as client:
            await self._create_tasks(data_list, client=client, **kwargs)

    async def task(self, stock, **kwargs):
        client = kwargs.get("client")
        if client and stock:
            stock_code = stock["stock_code"]
            start_time = stock["market_time"]
            page_index = kwargs.get("page_index")
            url = self._get_url()
            headers = self._get_headers()
            params = self._get_params(stock_code, start_time, self.pageSize, page_index)
            if page_index is None or page_index == 0:
                print("开始请求股票 %s" % stock_code)
            async with client.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json(encoding="utf-8")
                    await self._fr_parser_to_db(client, result, stock, stock_code, page_index + 1)
                else:
                    print("请求失败 错误码为%s" % response.status)
        else:
            print("client or stock 信息为None")

    async def _fr_parser_to_db(self, client, result, stock, stock_code, page_index):
        """
        解析财报信息，并存入数据库
        :param client: 同一个session
        :param result: 请求结果
        :param stock: 股票类
        :param stock_code: 股票代码
        :param page_index: 页面索引
        """
        if result:
            data_total_size = result[self.data_size_key]
            fr_data_list = result[self.data_key]
            new_fr_list = list()
            for fr in fr_data_list:
                title = str(fr[self.title_key])
                pdf_path = "%s%s" % (DPF_DOWNLOAD_BASE_URL, fr[self.pdf_path_key])
                if title.endswith("年年度报告") or title.endswith("年年度报告（更新后）") or title.endswith("年年度报告(更新后)"):
                    new_fr_list.append(self.table.create_table(
                        stock_code,
                        title,
                        pdf_path,
                        fr[self.pdf_size_key],
                        ""
                    ))
                else:
                    print("不符合要求的财报数据 标题为%s" % title)
            if len(new_fr_list) > 0:
                self.table.insert_many(new_fr_list)
                page_count = data_total_size / self.pageSize
                page_count = math.ceil(page_count)
                if page_index < page_count:
                    print("%s 股票开始第%s页面的请求，公共有%s页" % (stock_code, page_index, page_count))
                    await self.task(stock, client=client, page_index=page_index)
                else:
                    print("%s股票财报数据保存数据库完毕" % stock_code)
            else:
                print("插入数据的条数为0")
        else:
            print("请求结果为None")

    def start_download(self):
        from app.src.data.database.table.StockTable import StockTable
        stock_table = StockTable()
        stock_cursor = stock_table.find(filter={}, projection={
            "_id": 0,
            "stock_code": "0",
            "market_time": "0"
        })
        stock_list = [stock for stock in stock_cursor]
        print("需要请求的股票数量有%s" % len(stock_list))
        # 先清除表内容
        self.table.drop()
        # 开始请求数据
        self.run_tasks(stock_list)


AsyncFrDownload().start_download()
