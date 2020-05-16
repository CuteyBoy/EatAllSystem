import asyncio
import random
import os
import aiohttp as http
import abc


class AsyncRequest(metaclass=abc.ABCMeta):
    """
    数据工具类，主要封装数据的异步请求以及下载等操作
    """

    @abc.abstractmethod
    async def _success_handle(self, url, response):
        pass

    @abc.abstractmethod
    async def _fail_handle(self, url, error_code):
        pass

    async def _task(self, client, url, **kwargs):
        method = kwargs.get("method")
        if method is None or method == "GET":
            async with client.get(url, params=kwargs.get("params"), headers=kwargs.get("headers")) as response:
                error_code = response.status
                if error_code == 200:
                    await self._success_handle(url, response)
                else:
                    await self._fail_handle(url, error_code)
        else:
            async with client.post(url, data=kwargs.get("data"), headers=kwargs.get("headers")) as response:
                error_code = response.status
                if error_code == 200:
                    await self._success_handle(url, response)
                else:
                    await self._fail_handle(url, error_code)

    async def _start_request(self, urls, **kwargs):
        async with http.ClientSession(cookies=kwargs.get("cookies")) as client:
            task_list = None
            if isinstance(urls, list) and len(urls) > 0:
                task_list = [asyncio.create_task(self._task(client, url, **kwargs)) for url in urls]
            elif isinstance(urls, str) and len(urls) > 0:
                task_list = [asyncio.create_task(self._task(client, urls, **kwargs))]
            if task_list:
                await asyncio.gather(*task_list)

    def async_request(self, urls, **kwargs):
        """
        请求数据，该方法包括get和post请求数据
        :param urls: 请求地址，可以是一个请求列表，也可以是单个请求
        :param kwargs: 一些请求的参数，比如
        method=GET或POST;
        headers={}
        cookies={}
        POST请求的时候data=json
        GET请求的的时候参数params={}
        """
        asyncio.run(self._start_request(urls, **kwargs))


class XlsAsyncDownload(AsyncRequest):
    """
    使用协程进行股票的Xls异步下载，并将数据保存到数据库
    """

    async def _success_handle(self, url, response):
        save_path = "%s%s%s" % (os.getcwd(), os.sep, "sz_stock_all.xlsx")
        event_loop = asyncio.get_event_loop()

        def write_content(inner_file, inner_data):
            inner_file.write(inner_data)

        with open(save_path, 'wb') as file:
            while True:
                data = await response.content.read(1024)
                if not data:
                    break
                await event_loop.run_in_executor(None, write_content, file, data)
        print("url=%s 写完成" % url)

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
        self.async_request(url, params=params, headers=headers)


XlsAsyncDownload().download_to_db()
