import aiohttp
# from app.src.data.local.PdfParser import PdfParser
from app.src.data.local.Config import IndustryType
from app.src.data.database.table.StockTable import StockTable
from app.src.data.database.table.StockFrTable import StockFrTable
from app.src.data.remote.download.DataTools import AsyncTask, FileUtils


class AsyncDownload(AsyncTask, FileUtils):

    def __init__(self):
        super().__init__()
        self.fr_table = StockFrTable()

    async def task(self, data, **kwargs):
        if isinstance(data, list) and len(data) > 0:
            client = kwargs.get("client")
            if client:
                print("start task %s" % len(data))
                for stock in data:
                    stock_code = stock["stock_code"]
                    fr_stock = self.fr_table.find({
                                "code": stock_code
                            }).limit(1)
                    url = fr_stock[0]["pdf_path"]
                    fr_stock.close()
                    if url is None:
                        continue
                    async with client.get(url) as response:
                        request_code = response.status
                        if request_code == 200:
                            print("%s 请求成功, 开始写入")
                            await self._write_file(response, stock_code)
                        else:
                            print("%s 请求失败 错误码为%s" % (url, request_code))
            else:
                raise ValueError("client is None")

    async def _write_file(self, response, code):
        file_path = self.create_dir("cache")
        file_path = self.join("%s.PDF" % code, file_path)
        with open(file_path, "wb") as file:
            while True:
                # 读取响应内容
                data = await response.content.read(1024)
                if not data:
                    break
                # 异步写入内容
                file.write(data)
        # self._pdf_parser(file_path)

    # def _pdf_parser(self, file_path):
    #     with PdfParser.open(file_path) as pdf:
    #         pdf.start_parser()
    #     self.delete(file_path)

    async def package_tasks(self, data_list, **kwargs):
        async with aiohttp.ClientSession() as session:
            await self._create_tasks(data_list, client=session, **kwargs)

    def start(self):
        stock_table = StockTable()
        industry_list = IndustryType.get_all_type()
        task_list = list()
        for industry in industry_list:
            with stock_table.find(
                    filter={
                        "industry_type": industry.get_industry_type()
                    }).limit(2) as stock_list:
                if stock_list.count() > 0:
                    temp_stock_list = [stock for stock in stock_list]
                    task_list.append(temp_stock_list)
        if len(task_list) > 0:
            self.concurrent_num = 5
            self.run_tasks(task_list)
        else:
            print("task list is 0")


async_download = AsyncDownload()
async_download.start()
