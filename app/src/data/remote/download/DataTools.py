import asyncio
import aiohttp as http
import abc
import random
import os
from app.src.utils.TimeUtils import StockTimeUtils


class AsyncTask(metaclass=abc.ABCMeta):
    """
    封装使用协程来执行异步任务的抽象类
    """

    def __init__(self, concurrent_num=10):
        # 任务并发个数，默认是10
        self.concurrent_num = concurrent_num

    @abc.abstractmethod
    async def task(self, data, **kwargs):
        """
        子类需要实现的任务方法，在改方法内处理耗时任务
        :param data: 每个任务的数据
        :param kwargs: 其他需要参数
        """
        pass

    async def semaphore_task(self, data, semaphore, **kwargs):
        """
        并发执行多任务
        :param data: 数据
        :param semaphore 用于控制并发数量
        :param kwargs: 其他参数
        """
        if semaphore:
            async with semaphore:
                await self.task(data, **kwargs)
        else:
            await self.task(data, **kwargs)

    async def package_tasks(self, data_list, **kwargs):
        """
        子类需要调用create_tasks方法来进行重新组装任务列表
        :param data_list: 需要处理的数据列表
        :param kwargs: 其他需要的参数
        """
        await self._create_tasks(data_list, **kwargs)

    async def _create_tasks(self, data_list, **kwargs):
        """
        创建任务列表，由子类在package_tasks()方法中调用
        :param data_list: 需要处理的数据列表
        :param kwargs: 其他需要的参数，由上层决定，最终在task方法用到
        """
        if isinstance(data_list, list) and len(data_list) > 0:
            semaphore = asyncio.Semaphore(self.concurrent_num)
            task_list = [asyncio.create_task(self.semaphore_task(data, semaphore, **kwargs)) for data in data_list]
            await asyncio.gather(*task_list)
        else:
            print("数据列表是空，不需要创建任何任务")

    def run_tasks(self, data_list, **kwargs):
        """
        运行任务列表，需要自己主动调用运行
        :param data_list: 需要处理的数据列表
        :param kwargs: 其他需要的参数
        """
        if isinstance(data_list, list):
            data_list = self._split(data_list)
            if data_list:
                index = 0
                task_total_size = len(data_list)
                last_fail_index = kwargs.get("last_fail_index")
                if last_fail_index:
                    index = last_fail_index
                    data_list = data_list[last_fail_index: -1]
                else:
                    last_fail_index = 0
                print("任务总大小为%s" % task_total_size)
                for task_list in data_list:
                    try:
                        delay_des = "，延时0秒"
                        if index != last_fail_index:
                            interval_time = self.interval_time()
                            StockTimeUtils.sleep(interval_time)
                            delay_des = "，延时%s秒" % interval_time
                        print("开始执行第%s个任务%s" % (index + 1, delay_des))
                        asyncio.run(self.package_tasks(task_list, **kwargs))
                    except(KeyboardInterrupt, SystemExit):
                        print("退出所有的任务")
                        break
                    except Exception as e:
                        print("其他异常导致任务执行失败, 失败位置%s TimeoutError" % index, e)
                        break
                    index += 1

    def interval_time(self):
        """
        获取执行的间隔时间
        :return: 返回随机时间，单位是秒
        """
        return self.get_random_time(1, 5)

    @classmethod
    def get_random_time(cls, min_time, max_time):
        """
        返回随机时间，单位是秒
        :param min_time: 最小时间
        :param max_time: 最大时间
        :return: 随机时间，单位是秒
        """
        return random.randint(min_time, max_time)

    def _split(self, o_list):
        """
        将原列表切割成均等大小的小列表，如果原列表没有是数据，则返回None
        :param o_list: 原列表数据
        :return: 返回切割后的数据列表或者None
        """
        if isinstance(o_list, list):
            o_list_size = len(o_list)
            if o_list_size > 0:
                new_list = [o_list[i: i + self.concurrent_num] for i in range(0, o_list_size, self.concurrent_num)]
                return new_list
        return None


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
                    async with client.get(data, params=kwargs.get("params"),
                                          headers=kwargs.get("headers")) as response:
                        is_fail_handle = True
                        await self._result_handle(data, response)
                else:
                    # POST 请求方法
                    async with client.post(data, data=kwargs.get("data"),
                                           headers=kwargs.get("headers")) as response:
                        is_fail_handle = True
                        await self._result_handle(data, response)
        if is_fail_handle is False:
            # 处理错误的情况
            await self._result_handle(data)

    async def package_tasks(self, data_list, **kwargs):
        async with http.ClientSession(cookies=kwargs.get("cookies")) as client:
            # 重新组装任务列表
            await self._create_tasks(data_list, client=client, **kwargs)


class FileUtils(object):
    """
    文件工具类
    """

    def create_dir(self, dir_name):
        """
        在当前目录下面创建目录，如果目录没有存在
        :param dir_name:
        """
        dir_path = self.join(dir_name)
        if self.is_exist(dir_path) is False:
            os.mkdir(dir_path)
        return dir_path

    @classmethod
    def is_exist(cls, file):
        """
        判断给定的文件是否存在
        :param file: 需要检查的文件
        :return: True表示存在，否则表示不存在
        """
        return os.path.exists(file)

    @classmethod
    def join(cls, dir_name, start_dir=os.getcwd()):
        """
        将给的目录加入到当前的目录下面
        :param dir_name: 给定的目录名
        :param start_dir 开始目录
        :return: 返回链接的文件路径字符串
        """
        return os.path.join(start_dir, dir_name)

    @classmethod
    def write(cls, file_name, write_content, write_mode="wb"):
        """
        异步将指定内容写入指定文件
        :param file_name: 文件名
        :param write_content: 写入的内容
        :param write_mode: 打开模式，默认是"wb"
        """
        with open(file_name, write_mode) as file:
            file.write(write_content)

    @classmethod
    def isdir(cls, file):
        """
        判断是否目录
        :param file: 给的文件
        :return: True表示目录，否则不是
        """
        return os.path.isdir(file)

    @classmethod
    def isfile(cls, file):
        """
        判断是否文件
        :param file: 给定文件
        :return: True表示文件，否则不是
        """
        return os.path.isfile(file)

    def delete(self, file):
        """
        删除文件
        :param file: 文件
        """
        if self.is_exist(file):
            if self.isdir(file):
                os.rmdir(file)
            elif self.isfile(file):
                os.remove(file)
            else:
                raise ValueError("% is not file or dir" % file)

    def files(self, dir_path):
        """
        获取所有的指定目录下所有的文件路径
        :param dir_path: 指定的目录名路径
        :return: 所有文件路径
        """
        file_name_list = os.listdir(dir_path)
        return [self.join(file_name, dir_path) for file_name in file_name_list]
