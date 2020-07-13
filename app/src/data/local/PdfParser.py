import os
import re
import abc
import asyncio
from app.src.data.remote.download.DataTools import FileUtils, AsyncTask
from pdfplumber.pdf import PDF
from pdfplumber.page import Page
from pdfminer.pdfpage import PDFPage
from app.src.data.database.table.StockFrTable import StockFrTable


class ConditionBuilder(object):
    """
    条件构建器
    """

    def __init__(self):
        self.is_and_condition = False
        self.and_conditions = list()
        self.or_conditions = list()

    def and_builder(self, *args):
        self.is_and_condition = True
        if args:
            for condition in args:
                if condition not in self.and_conditions:
                    self.and_conditions.append(condition)

    def and_conditions_clear(self):
        self.and_conditions.clear()

    def or_builder(self, *args):
        self.is_and_condition = False
        if args:
            for condition in args:
                if condition not in self.or_conditions:
                    self.or_conditions.append(condition)

    def or_conditions_clear(self):
        self.or_conditions.clear()


class PdfFilter(object):
    """
    pdf 过滤器
    """

    def __init__(self):
        self.conditions = ConditionBuilder()

    def condition_run(self, builder, page_content):
        """
        条件执行方法
        :param builder: 当前的条件构建器
        :param page_content: 页面内容
        :return: 找到返回True，没有找到返回False
        """
        flag = builder.is_and_condition
        conditions = builder.and_conditions if flag else builder.or_conditions
        for condition in conditions:
            if isinstance(condition, list):
                inner_flag = True
                for single_c in condition:
                    if single_c not in page_content:
                        inner_flag = False
                        break
                if self.conditions.is_and_condition:
                    if inner_flag is False:
                        flag = False
                else:
                    if inner_flag:
                        flag = True
            elif isinstance(condition, ConditionBuilder):
                flag = self.condition_run(condition, page_content)
            else:
                if builder.is_and_condition:
                    if condition not in page_content:
                        flag = False
                else:
                    if condition in page_content:
                        flag = True
            if flag is not builder.is_and_condition:
                break
        return flag

    def or_conditions(self, *args):
        """
        构建or条件
        :param args: 条件
        """
        self.conditions.or_conditions_clear()
        self.conditions.or_builder(*args)

    def and_conditions(self, *args):
        """
        构建and条件
        :param args: 条件
        """
        self.conditions.and_conditions_clear()
        self.conditions.and_builder(*args)

    @classmethod
    def and_builder(cls, *args):
        """
        and 构建器
        :param args: 条件
        :return: 返回and构建对象
        """
        builder = ConditionBuilder()
        builder.and_builder(*args)
        return builder

    @classmethod
    def or_builder(cls, *args):
        """
        or 构建器
        :param args: 条件
        :return: 返回or构建器
        """
        builder = ConditionBuilder()
        builder.or_builder(*args)
        return builder

    def _find_table(self, page_content):
        """
        找表基本实现
        :param page_content: 页面内容
        :return: True表示找到
        """
        return self.condition_run(self.conditions, page_content)

    def find_debt_table(self, is_find_prefix, page_content):
        """
        该方法用来找到资产负债表
        :param is_find_prefix 是否找前缀
        :param page_content: 页面内容
        :return: True表示找到
        """
        if is_find_prefix:
            self.and_conditions(
                self.or_builder(
                    "资产负债表",
                    "合并资产负债表"
                ),
                self.or_builder(
                    self.and_builder(
                        "资产",
                        "现金及存放中央银行款项",
                        "资产总计",
                    ),
                    self.and_builder(
                        "流动资产",
                        "货币资金"
                    )
                )
            )
        else:
            self.or_conditions(
                "负债和所有者权益总计",
                "负债及股东权益总计"
            )
        return self._find_table(page_content)

    def find_profit_table(self, is_find_prefix, page_content):
        """
        该方法用来找到合并利润率表
        :param is_find_prefix 是否找前缀
        :param page_content: 页面内容
        :return: True表示找到
        """
        if is_find_prefix:
            self.and_conditions(
                self.or_builder(
                    "利润表",
                    "合并利润表"
                ),
                self.or_builder(
                    "一、营业收入",
                    "一、营业总收入"
                )
            )
        else:
            self.and_conditions(
                "稀释每股收益"
            )
        return self._find_table(page_content)

    def find_flow_table(self, is_find_prefix, page_content):
        """
        该方法用来找到现金流量表
        :param is_find_prefix 是否找前缀
        :param page_content: 页面内容
        :return: True表示找到
        """
        if is_find_prefix:
            self.and_conditions(
                self.or_builder(
                    "现金流量表",
                    "合并现金流量表"
                ),
                "经营活动现金流入小计"
            )
        else:
            self.or_conditions(
                "期末现金及现金等价物余额",
                "年末现金及现金等价物余额"
            )
        return self._find_table(page_content)


class AbstractPdfParser(PDF, metaclass=abc.ABCMeta):
    """
    抽象处于一个公共的PDF解析器
    """

    def __init__(self,
                 stream,
                 pages=None,
                 laparams=None,
                 precision=0.001,
                 password=""):
        super().__init__(stream, pages, laparams, precision, password)
        self.pdf_filter = PdfFilter()
        self.debt_table_start_index = -1
        self.debt_table_content = None
        self.profit_table_start_index = -1
        self.profit_table_content = None
        self.flow_table_start_index = -1
        self.flow_table_content = None

    def _is_find_table(self, page):
        """
        用于判断是否找到页面中的表
        :param page: 页面
        :return: True表示找到
        """
        return len(page.find_tables(self.get_table_setting())) > 0

    @abc.abstractmethod
    def on_find_debt_table(self, debt_table_content):
        """
        找到负债表内容
        :param debt_table_content: 负债表内容，准备解析
        """
        pass

    def _is_filter_table(self, table_type, start_index=-1, page_content=None):
        """
        用于筛选是否对应的表
        :param table_type: 表类型
        :param start_index: 开始找的位置
        :param page_content:  页面内容
        :return: 找到属于表内容的返回True，否则返回False
        """
        if table_type == 1:
            flag = self.pdf_filter.find_debt_table(start_index == -1, page_content)
        elif table_type == 2:
            flag = self.pdf_filter.find_profit_table(start_index == -1, page_content)
        else:
            flag = self.pdf_filter.find_flow_table(start_index == -1, page_content)
        return flag

    def _set_start_index(self, table_type, new_start_index):
        """
        设置表对应的索引位置
        :param table_type: 表类型
        :param new_start_index: 新的值
        """
        if table_type == 1:
            self.debt_table_start_index = new_start_index
        elif table_type == 2:
            self.profit_table_start_index = new_start_index
        else:
            self.flow_table_start_index = new_start_index

    def _set_content(self, table_type, is_add, new_content):
        """
        设置表内容
        :param table_type: 表类型
        :param is_add: 是否追加
        :param new_content: 表内容
        """
        if table_type == 1:
            self.debt_table_content = self.debt_table_content + new_content if is_add else new_content
        elif table_type == 2:
            self.profit_table_content = self.profit_table_content + new_content if is_add else new_content
        else:
            self.flow_table_content = self.flow_table_content + new_content if is_add else new_content

    def _set_callback(self, table_type):
        """
        设置回调
        :param table_type: 表类型
        """
        if table_type == 1:
            self.on_find_debt_table(self.debt_table_content)
        elif table_type == 2:
            self.on_find_profit_table(self.profit_table_content)
        else:
            self.on_find_flow_table(self.flow_table_content)

    def _find_table_filter(self, table_type, start_index=-1, page=None, page_content=None):
        """
        找表筛选器
        :param table_type: 表类型
        :param start_index: 索引位置
        :param page: 页面
        :param page_content: 页面内容
        """
        flag = self._is_filter_table(table_type, start_index, page_content)
        is_table = self._is_find_table(page)
        if flag and start_index == -1 and is_table:
            start_index = 1
            self._set_start_index(table_type, start_index)
            self._set_content(table_type, False, page_content)
            flag = self._is_filter_table(table_type, start_index, page_content)
            start_index = 2 if flag else 1
            self._set_start_index(table_type, start_index)
        elif start_index == 1 and flag is False:
            self._set_content(table_type, True, page_content)
        elif start_index == 1 and flag and is_table:
            start_index = 2
            self._set_start_index(table_type, start_index)
            self._set_content(table_type, True, page_content)
        if start_index == 2:
            self._set_start_index(table_type, 3)
            self._set_callback(table_type)

    @abc.abstractmethod
    def on_find_profit_table(self, profit_table_content):
        """
        找到利润表
        :param profit_table_content: 利润表内容
        """
        pass

    @abc.abstractmethod
    def on_find_flow_table(self, flow_table_content):
        """
        找到现金流量表
        :param flow_table_content: 表内容
        """
        pass

    @classmethod
    def _get_key_pattern(cls, key):
        return "%s.*" % key

    @classmethod
    def _get_value_pattern(cls):
        return "\(*-*\d{1,3}(?:,\d{3})*\.\d*\)*"

    @classmethod
    def get_project_pattern(cls):
        return "[^\d]+(?=\s)"

    def get_match_list(self, table_content):
        """
        使用正则表达式获取所有匹配的内容
        :param table_content: 需要进行匹配的内容
        :return: 返回匹配列表
        """
        return re.findall(self.get_project_pattern(), table_content)

    @classmethod
    def get_table_setting(cls, **kwargs):
        """
        获取筛选表设置参数
        :param kwargs: 可选参数设置，比如vertical_strategy和vertical_strategy
        :return: 返回默认的参数字典对象
        """
        vertical_strategy = kwargs.get("vertical_strategy")
        vertical_strategy = vertical_strategy if vertical_strategy else "text"
        horizontal_strategy = kwargs.get("horizontal_strategy")
        horizontal_strategy = horizontal_strategy if horizontal_strategy else "text"
        return {
            "vertical_strategy": vertical_strategy,
            "horizontal_strategy": horizontal_strategy,
            "explicit_vertical_lines": [],
            "explicit_horizontal_lines": [],
            "snap_tolerance": 3,
            "join_tolerance": 3,
            "edge_min_length": 3,
            "min_words_vertical": 1,
            "min_words_horizontal": 1,
            "keep_blank_chars": False,
            "text_tolerance": 3,
            "text_x_tolerance": None,
            "text_y_tolerance": None,
            "intersection_tolerance": 3,
            "intersection_x_tolerance": None,
            "intersection_y_tolerance": None
        }

    def start_parser(self):
        """
        该方法暴露开始解析目标页面的数据，解析后的数据进行存入数据库
        可以很方便的进行一边解析，一边扫描满足需要的股票
        """
        print("start parser")
        doc_top = 0
        # 将pdf加载到内存
        page_doc_list = enumerate(PDFPage.create_pages(self.doc))
        for index, page_doc in page_doc_list:
            # 生存页面对象，方便解析
            page = Page(self, page_doc, page_number=index + 1, initial_doctop=doc_top)
            is_finish_parser = self._page_parser(page, page.extract_text())
            if is_finish_parser:
                # 说明所有需要的表都找到了，直接退出
                break
            doc_top += page.height

    def _page_parser(self, page, page_text):
        """
        页面解析器
        :param page: 页面
        :param page_text 页面文本
        :return: 返回True表是退出解析器，False表示继续解析
        """
        is_end_flag = False
        if self.debt_table_start_index < 3:
            self._find_table_filter(1, self.debt_table_start_index, page, page_text)
        elif self.profit_table_start_index < 3:
            self._find_table_filter(2, self.profit_table_start_index, page, page_text)
        elif self.flow_table_start_index < 3:
            self._find_table_filter(3, self.flow_table_start_index, page, page_text)
        else:
            is_end_flag = True
        return is_end_flag


class PdfParserImpl(AbstractPdfParser):
    """
    通用的PDF解析器的实现类
    """

    def __init__(self,
                 stream,
                 pages=None,
                 laparams=None,
                 precision=0.001,
                 password=""):
        super().__init__(stream, pages, laparams, precision, password)

    def project_name_list(self, content, error_hint):
        project_list = self.get_match_list(content)
        project_list_size = len(project_list)
        if project_list_size > 0:
            for project in project_list:
                project = str(project).replace(" ", "")
                if len(project) > 0:
                    print(project)
        else:
            print("未找到%s表内容" % error_hint)

    def on_find_debt_table(self, debt_table_content):
        self.project_name_list(debt_table_content, "负债表")

    def on_find_profit_table(self, profit_table_content):
        self.project_name_list(profit_table_content, "利润表")

    def on_find_flow_table(self, flow_table_content):
        self.project_name_list(flow_table_content, "流量表")


class MultiPdfParser(AsyncTask):

    async def task(self, data, **kwargs):
        loop = asyncio.get_event_loop()

        def read_pdf_and_parser():
            with PdfParserImpl.open(data) as pdf:
                pdf.start_parser()

        await loop.run_in_executor(None, read_pdf_and_parser)

    def interval_time(self):
        return 0

    def run_parser(self):
        """
        扫描pdf文件
        """
        cache_dir_name = "/Users/robot/PycharmProjects/EatAllSystem/app/src/data/remote/download/cache"
        file_list = FileUtils().files(cache_dir_name)
        self.run_tasks(file_list)


multi_pdf_parser = MultiPdfParser()
multi_pdf_parser.run_parser()

