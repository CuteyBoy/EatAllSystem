import aiohttp
import time
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
                    with self.fr_table.find(
                            filter={
                                "code": stock["stock_code"]
                            }).limit(1) as fr_stock:
                        url = fr_stock["pdf_path"]
                        print("url=", url)
                        if url is None:
                            continue
                        async with client.get(url) as response:
                            if response.status == 200:
                                print("url=%s status=%s" % (url, response.status))
                                await self._write_file(response)
            else:
                raise ValueError("client is None")

    async def _write_file(self, response):
        file_path = self.join("%s.PDF" % time.time())
        if self.is_exist(file_path):
            with open(file_path, "wb") as file:
                while True:
                    # 读取响应内容
                    data = await response.content.read(1024)
                    if not data:
                        break
                    # 异步写入内容
                    file.write(data)

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
