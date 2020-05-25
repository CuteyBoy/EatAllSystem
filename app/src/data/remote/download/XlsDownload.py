import random
import os
import re
import asyncio
import pandas as pd
from app.src.data.local.Config import MarketType
from app.src.data.local.Config import IndustryType
from app.src.data.database.table.StockTable import StockTable
from app.src.data.remote.download.DataTools import AsyncRequest


class XlsDownload(AsyncRequest):
    """
    使用协程进行股票的Xls异步下载，并将数据保存到数据库
    """
    def __init__(self, market_type=MarketType.SZ):
        super().__init__()
        self.market_type = market_type
        self.table = StockTable()
        self.xls_save_path = "%s%s%s" % (os.getcwd(), os.sep, "sz_stock_all.xlsx")

    async def _success_handle(self, url, response):
        event_loop = asyncio.get_event_loop()

        # 定义一个写的方法来实现异步写入
        def write_content(inner_file, inner_data):
            inner_file.write(inner_data)

        # 打开需要保存的文件
        with open(self.xls_save_path, 'wb') as file:
            while True:
                # 读取响应内容
                data = await response.content.read(1024)
                if not data:
                    break
                # 异步写入内容
                await event_loop.run_in_executor(None, write_content, file, data)
        # 重新读取文件并保存到数据库
        await event_loop.run_in_executor(None, self._save_to_db)

    def _save_to_db(self):
        """
        重新读取去读文本并保存到数据库
        """
        # 先删除之前的表
        self.table.drop()
        read_column_list = ["公司代码", "公司简称", "A股上市日期", "A股总股本", "A股流通股本", "城     市", "所属行业", "公司网址"]
        # 读取数据
        data_frame = pd.read_excel(self.xls_save_path, dtype=object)
        # 取出需要的数据
        data_frame = data_frame.loc[:, read_column_list]
        stock_list = list()
        for row in data_frame.itertuples():
            # 判断是否满足条件，避免造成取数据索引越界
            if len(row) >= 8:
                # 用正则表达式匹配出行业名
                industry_name = re.findall(r'(?<=\s)\S+', row[7])
                if industry_name and len(industry_name) > 0:
                    # 获取到行业名
                    industry_name = industry_name[0]
                    # 创建数据库实现对象
                    stock_list.append(self.table.create_table(
                        self.market_type.get_market_type(),
                        row[1],
                        row[2],
                        row[3],
                        IndustryType.get_type_by_name(industry_name),
                        industry_name,
                        str(row[4]).replace(",", ""),
                        str(row[5]).replace(",", ""),
                        row[6],
                        row[8]
                    ))
                else:
                    print("该 %s 股票由于找属于行业名失败，导致未插入数据库" % row[1])
            else:
                print("该行不满足个数，%s" % row)
        # 判断是否需要进行插入数据库操作
        if len(stock_list) > 0:
            # 将新的数据插入数据
            self.table.insert_many(stock_list)

    async def _fail_handle(self, url, error_code):
        print("error_code=%s url=%s" % (error_code, url))

    def download_to_db(self):
        """
        开始下载并保存到数据库的方法
        """
        url = "http://www.szse.cn/api/report/ShowReport"
        params = {
            "SHOWTYPE": "xlsx",
            "CATALOGID": "1110",
            "TABKEY": "tab1",
            "random": "%s" % random.random()
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image"
                      "/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/80.0.3987.163 Safari/537.36",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "http://www.szse.cn/market/stock/list/index.html",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.run_tasks([url], params=params, headers=headers)
