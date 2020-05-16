import os
import re
from pdfplumber.pdf import PDF
from pdfplumber.page import Page
from pdfminer.pdfpage import PDFPage
from data.database.table.StockFrTable import StockFrTable


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
            self.and_conditions(
                "现金及现金等价物净增加"
            )
        return self._find_table(page_content)


class PdfParser(PDF):

    def __init__(self,
                 stream,
                 pages=None,
                 laparams=None,
                 precision=0.001,
                 password=""):
        super().__init__(stream, pages, laparams, precision, password)
        self.filter = PdfFilter()
        self.debt_table_start_index = -1
        self.debt_table_content = None
        self.profit_table_start_index = -1
        self.profit_table_content = None
        self.flow_table_start_index = -1
        self.flow_table_content = None

    def _find_debt_table(self, page_content):
        """
        找负债表所有内容
        :param page_content: 页面
        """
        flag = self.filter.find_debt_table(self.debt_table_start_index == -1, page_content)
        if flag and self.debt_table_start_index == -1:
            self.debt_table_start_index = 1
            self.debt_table_content = page_content
        elif self.debt_table_start_index == 1 and flag is False:
            self.debt_table_content += page_content
        elif self.debt_table_start_index == 1 and flag:
            self.debt_table_start_index = 2
            self.debt_table_content += page_content
        if self.debt_table_start_index == 2:
            self.debt_table_start_index = 3
            self._parser_debt_table()

    def _find_profit_table(self, page_content):
        """
        找利润表所有内容
        :param page_content: 所有利润表内容
        """
        flag = self.filter.find_profit_table(self.profit_table_start_index == -1, page_content)
        if flag and self.profit_table_start_index == -1:
            self.profit_table_start_index = 1
            self.profit_table_content = page_content
        elif self.profit_table_start_index == 1 and flag is False:
            self.profit_table_content += page_content
        elif self.profit_table_start_index == 1 and flag:
            self.profit_table_start_index = 2
            self.profit_table_content += page_content
        if self.profit_table_start_index == 2:
            self.profit_table_start_index = 3
            self._parser_profit_table()

    def _find_flow_table(self, page_content):
        flag = self.filter.find_flow_table(self.flow_table_start_index == -1, page_content)
        if flag and self.flow_table_start_index == -1:
            self.flow_table_start_index = 1
            self.flow_table_content = page_content
        elif self.flow_table_start_index == 1 and flag is False:
            self.flow_table_content += page_content
        elif self.flow_table_start_index == 1 and flag:
            self.flow_table_start_index = 2
            self.flow_table_content += page_content
        if self.flow_table_start_index == 2:
            self.flow_table_start_index = 3
            self._parser_flow_table()

    @classmethod
    def _get_key_pattern(cls, key):
        return "%s.*" % key

    @classmethod
    def _get_value_pattern(cls):
        return "\(*-*\d{1,3}(?:,\d{3})*\.\d*\)*"

    def _parser_debt_table(self):
        """
        解析负债表数据
        @:param page_content: 页面内容
        """
        pattern = "[^\d]+(?=\s)"
        result_list = re.findall(pattern, self.debt_table_content)
        if result_list:
            for result in result_list:
                print(result)
        # params = ["(股东权益合计|所有者权益合计)",
        #           "负债总计|负债合计",
        #           "短期借款",
        #           "长期借款"
        #           ]
        # for key in params:
        #     result_list = re.findall(self._get_key_pattern(key), self.debt_table_content)
        #     if len(result_list) > 0:
        #         result_list = re.findall(self._get_value_pattern(), result_list[0])
        #         if len(result_list) > 0:
        #             for result in result_list:
        #                 print("%s=%s" % (key, result.replace(",", "")))

    def _parser_profit_table(self):
        """
        解析利润表数据
        @:param page_content: 页面内容
        """
        pattern = "[^\d]+(?=\s)"
        result_list = re.findall(pattern, self.profit_table_content)
        if result_list:
            for result in result_list:
                print(result)
        # print("利润表=", self.profit_table_content)

    def _parser_flow_table(self):
        """
        解析现金流量表
        @:param page_content: 页面内容
        """
        # print("流量表=", self.flow_table_content)
        pattern = "[^\d]+(?=\s)"
        result_list = re.findall(pattern, self.flow_table_content)
        if result_list:
            for result in result_list:
                print(result)

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
            # 将当前页面进行转文本
            page_content = page.extract_text()
            self._find_debt_table(page_content)
            self._find_profit_table(page_content)
            self._find_flow_table(page_content)
            if self.flow_table_start_index >= 3:
                # 说明所有需要的表都找到了，直接退出
                break
            doc_top += page.height


def scan_pdf():
    # 000428
    # 002053
    # 300661
    fr_table = StockFrTable()
    fr_list = fr_table.find({
        "code": "000428"
    }).limit(1)
    for fr in fr_list:
        pdf_path = fr["local_pdf_path"]
        if pdf_path and os.path.exists(pdf_path):
            with PdfParser.open(pdf_path) as pdf:
                pdf.start_parser()


# scan_pdf()
# pdf_parser = PdfFilter()

# page_content_list = [
#     "1,==========经营活动现金流入小计3",
#     "2合并现金流量表 (续),0000==========筹资活动现金流入小计3 9999",
#     "合并现2金流量表,==========筹资9活动现金流入小计",
#     "合并现2金流量表,==========-==========9===0000===9999",
#     "合并现金",
# ]
#
# pdf_parser.and_conditions(
#     pdf_parser.or_builder(
#         pdf_parser.and_builder(["1", "3"]),
#         pdf_parser.and_builder(["2", "3"]),
#         pdf_parser.and_builder(["2", "9"])
#     ),
#     pdf_parser.and_builder(["0000", "9999"])
# )
# for temp_content in page_content_list:
#     print(pdf_parser.condition_run(pdf_parser.conditions, temp_content))
# result = re.findall("(?<=\s)\S+", data[7])
path = "%s%sstocks%s%s" % (os.getcwd(), os.sep, os.sep, "sz_all_market_company.xlsx")
pd_frame = pd.read_excel(path)
pd_frame_d = pd_frame.loc[:, ["公司代码", "公司简称", "A股上市日期", "A股总股本", "A股流通股本", "城     市", "所属行业", "公司网址"]]
for data in pd_frame_d.itertuples():
    print(data)
