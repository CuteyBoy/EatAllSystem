import asyncio
import aiohttp as http
import abc


class AsyncRequest(metaclass=abc.ABCMeta):
    """
    数据工具类，主要封装数据的异步请求以及下载等操作
    """

    @abc.abstractmethod
    async def _success_handle(self, url, response):
        """
        数据请求成功走该方法，需要子类取继承实现
        :param url: 请求成功的连接地址
        :param response: 返回的响应体
        """
        pass

    @abc.abstractmethod
    async def _fail_handle(self, url, error_code):
        """
        请求失败需要的走的方法，需要子类自己实现
        :param url: 请求失败的地址
        :param error_code: 错误码
        """
        pass

    async def _result_handle(self, url, response):
        """
        结果通过在该方法中进行处理
        :param url: 请求地址
        :param response: 请求响应体
        """
        error_code = response.status
        if error_code == 200:
            # 请求成功子类需要处理的
            await self._success_handle(url, response)
        else:
            # 请求失败子类需要处理的
            await self._fail_handle(url, error_code)

    async def _task(self, client, url, **kwargs):
        """
        协程需要执行的任务方法，该方法主要是用来实现请求数据，包括get或post请求
        :param client: session对象
        :param url: 请求地址
        :param kwargs: 请求需要其他参数
        比如参数method
        get请求的params={"key": 000}
        headers={"Connection":"0"}
        post请求的data=json字符串
        """
        method = kwargs.get("method")
        if method is None or method == "GET":
            async with client.get(url, params=kwargs.get("params"), headers=kwargs.get("headers")) as response:
                await self._result_handle(url, response)
        else:
            async with client.post(url, data=kwargs.get("data"), headers=kwargs.get("headers")) as response:
                await self._result_handle(url, response)

    async def _start_request(self, urls, **kwargs):
        """
        该方法用来组装任务，比如urls如何是一个list需要调用_task创建异步任务
        :param urls: 这个参数可以传一个url或者list类型的url
        :param kwargs: 可以选参数
        """
        async with http.ClientSession(cookies=kwargs.get("cookies")) as client:
            task_list = None
            if isinstance(urls, list) and len(urls) > 0:
                # 创建多个任务
                task_list = [asyncio.create_task(self._task(client, url, **kwargs)) for url in urls]
            elif isinstance(urls, str) and len(urls) > 0:
                # 创建单个任务
                task_list = [asyncio.create_task(self._task(client, urls, **kwargs))]
            if task_list:
                # 一起提交执行任务
                await asyncio.gather(*task_list)

    def async_request(self, urls, **kwargs):
        """
        异步请求数据，该方法包括get和post请求数据
        :param urls: 请求地址，可以是一个请求列表，也可以是单个请求
        :param kwargs: 一些请求的参数，比如
        method=GET或POST;
        headers={}
        cookies={}
        POST请求的时候data=json
        GET请求的的时候参数params={}
        """
        asyncio.run(self._start_request(urls, **kwargs))
