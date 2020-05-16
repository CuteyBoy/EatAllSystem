import random
import json
import math
from utils.TimeUtils import StockTimeUtils
from data.remote.download.AbsDownload import AbsDownload

# pdf下载基础地址
DPF_DOWNLOAD_BASE_URL = "http://disc.static.szse.cn/download"


class StockFrDownload(AbsDownload):
    """
       用于封装股票对应的财报信息数据
       """

    def __init__(self):
        from data.database.table.StockFrTable import StockFrTable
        super().__init__(StockFrTable())
        self.pageSize = 30
        self.fr_pdf_path_key = "attachPath"
        self.fr_title_key = "title"
        self.fr_pdf_size_key = "attachSize"
        self.data_all_size_key = "announceCount"

    def _get_url(self, **kwargs):
        return "http://www.szse.cn/api/disc/announcement/annList?random=%s" % random.random()

    def _get_headers(self, **kwargs):
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

    def _get_params(self, **kwargs):
        """
        @:param start_time 开始时间，比如"2014-12-01"
        @:param end_time 结束时间 比如"2020-04-19"
        @:param code 股票代码
        @:param page_index 请求的页面索引值
        :param args:
        :param kwargs:
        :return:
        """
        code = kwargs["code"]
        start_time = kwargs["start_time"]
        end_time = kwargs["end_time"]
        page_index = kwargs["page_index"]
        params = {
            "seDate": [start_time if start_time else "", end_time if end_time else ""],
            "stock": [code if code else "000001"],
            "channelCode": ["fixed_disc"],
            "bigCategoryId": ["010301"],
            "pageSize": self.pageSize,
            "pageNum":  page_index if page_index else 1
        }
        return json.dumps(params)

    def filter(self):
        """
        过滤调不需要的数据
        :return:
        """
        from data.database.table.StockTable import AllStockTable
        all_stock_table = AllStockTable()
        all_stock_list = all_stock_table.find(filter={}, projection={
            "_id": 0,
            "code": 1,
        })
        print("code_size=%s" % all_stock_list.count())
        for stock in all_stock_list:
            all_fr_data = self.table.find(filter={"code": stock["code"]})
            print("fr_size=%s" % (all_fr_data.count()))
            for fr in all_fr_data:
                title = str(fr["title"])
                if title.endswith("年年度报告") is False or title.endswith("年年度报告（更新后）") is False:
                    count = self.table.delete_many({"_id": fr["_id"]})
                    print("delete count=%s" % count)

    def download_to_db(self, **kwargs):
        from data.database.table.StockTable import AllStockTable
        stock_all_table = AllStockTable()
        stock_code_list = stock_all_table.find(filter={}, projection={
            "_id": 0,
            "code": "0"
        })
        start_time = StockTimeUtils.get_start_time()
        end_time = StockTimeUtils.get_now_time_str()
        old_code = kwargs.get("old_code")
        is_next_download = False
        if old_code is None:
            self.table.drop()
        index = 0
        for stock in stock_code_list:
            if (old_code and is_next_download) or old_code is None:
                self._start_download(stock["code"], start_time, end_time, 1)
            else:
                print("downloaded stock code %s" % stock["code"])
            if old_code and old_code == stock["code"] and is_next_download is False:
                is_next_download = True
            index += 1
            print("downloaded stock count %s" % index)

    def _start_download(self, code, start_time, end_time, page_index):
        """
        递归进行下载对应公司的财报连接数据
        :param code:  股票代码
        :param start_time: 开始时间
        :param end_time: 结束时间，就是现在的时间
        :param page_index: 请求页面位置
        :return:
        """
        result = self.post_request_result(
            code=code,
            start_time=start_time,
            end_time=end_time,
            page_index=page_index
        )
        if result:
            result = result.json()
            data_total_size = result[self.data_all_size_key]
            fr_data_list = result[self.data_key]
            new_fr_list = list()
            for fr in fr_data_list:
                title = str(fr[self.fr_title_key])
                if title.endswith("年年度报告") or title.endswith("年年度报告（更新后）")\
                        or title.endswith("年年度报告(更新后)"):
                    print("code title=", title)
                    new_fr_list.append(self.table.create_table(
                        code,
                        fr[self.fr_title_key],
                        "%s%s" % (DPF_DOWNLOAD_BASE_URL, fr[self.fr_pdf_path_key]),
                        fr[self.fr_pdf_size_key],
                        ""
                    ))
            if len(new_fr_list) > 0:
                self.table.insert_many(new_fr_list)
                last_count = data_total_size / self.pageSize
                last_count = math.ceil(last_count)
                if page_index < last_count:
                    StockTimeUtils.sleep(2)
                    self._start_download(code, start_time, end_time, page_index + 1)
                else:
                    print("%s fr data save end" % code)
            else:
                self.d("%s fr data download end" % code)
        else:
            self.d("%s fr data download error" % code)
