import time
import random
from app.src.data.remote.download.AbsDownload import AbsDownload


class StockCodeAllDownload(AbsDownload):
    """
    实现所有的股票的代码的下载
    """

    def __init__(self, exchange_type="sz"):
        from app.src.data.database.table.StockTable import StockTable
        super().__init__(StockTable())
        self.exchange_type = exchange_type
        self.metadata_key = "metadata"
        self.page_count_key = "pagecount"
        self.code_key = "zqdm"
        self.name_key = "agjc"
        self.industry_type_key = "sshymc"
        self.start_time_key = "agssrq"

    def _get_url(self, **kwargs):
        return "http://www.szse.cn/api/report/ShowReport/data"

    def _get_headers(self, **kwargs):
        return {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/80.0.3987.163 Safari/537.36",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": "CASTGC=TGT-477-dIxsAc1g1gRKtYb3G2ioR2tOWxB2tw9PfxZpMlGCmHnujZxVGi-cas01.example.org; "
                      "JSESSIONID=719b57a5-9054-4912-b070-626d18709c1e",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-Request-Type": "ajax",
            "Referer": "http://www.szse.cn/market/stock/list/index.html"
        }

    def _get_params(self, **kwargs):
        return {"SHOWTYPE": "JSON",
                "CATALOGID": "1110",
                "TABKEY": "tab1",
                "PAGENO": kwargs["page_no"],
                "random": random.random()
                }

    def _start_download_to_db(self, current_page):
        """
        开始下载数据并保存到数据库
        :param current_page: 当前下载的页面数量
        :return:
        """
        print("downloading current_page=%s" % current_page)
        result = self.get_request_result(page_no=current_page)
        if result:
            result = result.json()[0]
            metadata = result[self.metadata_key]
            data = result[self.data_key]
            page_count = metadata[self.page_count_key]
            print("download page count is %s" % page_count)
            temp_stock_list = list()
            for stock in data:
                temp_table = self.table.create_table(
                    self.exchange_type,
                    stock[self.code_key],
                    stock[self.name_key],
                    stock[self.start_time_key],
                    stock[self.industry_type_key],
                )
                if temp_table:
                    temp_stock_list.append(temp_table)
            if len(temp_stock_list) > 0:
                self.table.insert_many(temp_stock_list)
            if current_page < page_count:
                time.sleep(random.randint(1, 6))
                self._start_download_to_db(current_page + 1)
            else:
                print("download end")
        else:
            print("download result is null")

    def download_to_db(self, **kwargs):
        self.table.drop()
        self._start_download_to_db(1)
