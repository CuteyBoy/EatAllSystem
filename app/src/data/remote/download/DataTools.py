import asyncio
import aiohttp as http
import abc


class AsyncTask(metaclass=abc.ABCMeta):
    """
    封装使用协程来执行异步任务的抽象类
    """

    @abc.abstractmethod
    async def task(self, data, **kwargs):
        """
        子类需要实现的任务方法，在改方法内处理耗时任务
        :param data: 每个任务的数据
        :param kwargs: 其他需要参数
        """
        pass

    @abc.abstractmethod
    async def package_tasks(self, data_list, **kwargs):
        """
        子类需要调用create_tasks方法来进行重新组装任务列表
        :param data_list: 需要处理的数据列表
        :param kwargs: 其他需要的参数
        """
        pass

    async def create_tasks(self, data_list, **kwargs):
        """
        创建任务列表，由子类在package_tasks()方法中调用
        :param data_list: 需要处理的数据列表
        :param kwargs: 其他需要的参数，由上层决定，最终在task方法用到
        """
        if isinstance(data_list, list) and len(data_list) > 0:
            task_list = [asyncio.create_task(self.task(data, **kwargs)) for data in data_list]
            await asyncio.gather(*task_list)
        else:
            print("数据列表是空，不需要创建任何任务")

    def run_tasks(self, data_list, **kwargs):
        """
        运行任务列表，需要自己主动调用运行
        :param data_list: 需要处理的数据列表
        :param kwargs: 其他需要的参数
        """
        asyncio.run(self.package_tasks(data_list, **kwargs))


class AsyncRequest(AsyncTask):
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

    async def _result_handle(self, url, response=None):
        """
        结果通过在该方法中进行处理
        :param url: 请求地址
        :param response: 请求响应体
        """
        error_code = response.status if response else -200
        if error_code == 200:
            # 请求成功子类需要处理的
            await self._success_handle(url, response)
        else:
            # 请求失败子类需要处理的
            await self._fail_handle(url, error_code)

    async def task(self, data, **kwargs):
        client = kwargs.get("client")
        is_fail_handle = False
        if client:
            # 请求地址不为空才进行下面的处理
            if data:
                # 获取请求类型
                method = kwargs.get("method")
                if method is None or method == "GET":
                    # GET请求方法
                    async with client.get(data, params=kwargs.get("params"), headers=kwargs.get("headers")) as response:
                        is_fail_handle = True
                        await self._result_handle(data, response)
                else:
                    # POST 请求方法
                    async with client.post(data, data=kwargs.get("data"), headers=kwargs.get("headers")) as response:
                        is_fail_handle = True
                        await self._result_handle(data, response)
        if is_fail_handle is False:
            # 处理错误的情况
            await self._result_handle(data)

    async def package_tasks(self, data_list, **kwargs):
        async with http.ClientSession(cookies=kwargs.get("cookies")) as client:
            # 重新组装任务列表
            await self.create_tasks(data_list, client=client, **kwargs)

