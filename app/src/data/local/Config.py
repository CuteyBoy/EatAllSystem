import re
from enum import Enum


class TablePeriod(Enum):
    """
    财报周期枚举类
    """

    def __init__(self, table_period, table_period_name):
        self._table_period = table_period
        self._table_period_name = table_period_name

    def get_table_period(self):
        """
        获取表周期类型
        :return: 返回1，2，3，4
        """
        return self._table_period

    def get_table_period_name(self):
        """
        获取周期类型名
        :return: 比如一季度报，二季度报，半年报，年报
        """
        return self._table_period_name

    # 第一季度财报类型
    FIRST_QUARTER_REPORT = (1, "一季度报")
    # 第一季度财报类型
    SECOND_QUARTER_REPORT = (2, "二季度报")
    # 第三季度财报类型
    THREE_QUARTER_REPORT = (3, "半年报")
    # 第四季度财报类型
    FOUR_QUARTER_REPORT = (4, "年报")


class MarketType(Enum):
    """
    市场类型，目前只考虑上交所和深交所，其他后期在家
    """
    def __init__(self, m_type, market_name):
        self._type = m_type
        self._market_name = market_name

    def get_market_type(self):
        """
        获取市场类型
        :return: 市场类型
        """
        return self._type

    def get_market_name(self):
        """
        获取市场类型名
        :return: 返回市场类型名
        """
        return self._market_name

    # 深圳交易所
    SZ = ("sz", "深交所")
    # 上海交易交易所
    SH = ("sh", "上交所")


class FrTableType(Enum):
    """
    财报类型（负债表、利润表、现金流量表）
    """

    def __init__(self, fr_type, table_name):
        self._type = fr_type
        self._table_name = table_name

    def get_table_type(self):
        """
        获取表类型
        :return: 类型
        """
        return self._type

    def get_table_name(self):
        """
        获取财报名
        :return: 财报名
        """
        return self._table_name

    # 合并负债表
    MERGE_DEBT_TABLE = (1, "合并负债表")
    # 母公司负债表
    PARENT_DEBT_TABLE = (2, "母公司负债表")
    # 合并利润表
    MERGE_PROFIT_TABLE = (3, "合并利润表")
    # 母公司利润表
    PARENT_PROFIT_TABLE = (4, "母公司利润表")
    # 合并现金流量表
    MERGE_CASH_FLOW_TABLE = (5, "合并现金流量表")
    # 母公司现金流量表
    PARENT_CASH_FLOW_TABLE = (6, "母公司现金流量表")


class IndustryType(Enum):
    """
    用于行业类型转换
    """

    def __init__(self, industry_type, industry_des_list):
        self._industry_type = industry_type
        self._industry_des_list = industry_des_list

    @staticmethod
    def get_type_by_name(industry_name):
        if IndustryType._check_industry_name(industry_name, IndustryType.AGRICULTURAL_FAH_FISHERY):
            return IndustryType.AGRICULTURAL_FAH_FISHERY.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.MINING_INDUSTRY):
            return IndustryType.MINING_INDUSTRY.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.MANUFACTURING):
            return IndustryType.MANUFACTURING.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.WATER_ELECTRICITY_GAS):
            return IndustryType.WATER_ELECTRICITY_GAS.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.CONSTRUCTION_INDUSTRY):
            return IndustryType.CONSTRUCTION_INDUSTRY.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.WHOLESALE_RETAIL):
            return IndustryType.WHOLESALE_RETAIL.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.TRANSPORTATION_STORAGE):
            return IndustryType.TRANSPORTATION_STORAGE.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.ACCOMMODATION):
            return IndustryType.ACCOMMODATION.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.INFORMATION_TECHNOLOGY):
            return IndustryType.INFORMATION_TECHNOLOGY.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.FINANCIAL_INDUSTRY):
            return IndustryType.FINANCIAL_INDUSTRY.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.REAL_ESTATE_INDUSTRY):
            return IndustryType.REAL_ESTATE_INDUSTRY.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.BUSINESS_SERVICES):
            return IndustryType.BUSINESS_SERVICES.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.RESEARCH_SERVICE):
            return IndustryType.RESEARCH_SERVICE.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.PUBLIC_ENVIRONMENTAL_PROTECTION):
            return IndustryType.PUBLIC_ENVIRONMENTAL_PROTECTION.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.RESIDENT_SERVICE):
            return IndustryType.RESIDENT_SERVICE.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.EDUCATION_INDUSTRY):
            return IndustryType.EDUCATION_INDUSTRY.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.HEALTH_INDUSTRY):
            return IndustryType.HEALTH_INDUSTRY.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.CULTURAL_COMMUNICATION):
            return IndustryType.CULTURAL_COMMUNICATION.get_industry_type()
        if IndustryType._check_industry_name(industry_name, IndustryType.COMPREHENSIVE):
            return IndustryType.COMPREHENSIVE.get_industry_type()

    @staticmethod
    def _check_industry_name(industry_name, industry_type):
        """
        检查列表中是否包含行业页面，使用正则进行匹配
        :param industry_name: 需要检查的行业名称
        :param industry_type: 行业类型
        :return: 包含返回True
        """
        industry_des_list = industry_type.get_names()
        if isinstance(industry_des_list, list):
            for industry_des in industry_des_list:
                result_list = re.findall(industry_name, industry_des)
                if result_list and len(result_list) > 0:
                    return True
        return False

    def get_industry_type(self):
        """
        获取行业的类型值
        :return: 返回行业类型
        """
        return self._industry_type

    def get_names(self):
        """
        获取行业的类型名
        :return: 类型名
        """
        return self._industry_des_list

    @staticmethod
    def get_all_type():
        """
        获取所有的类型列表
        :return: 返回对应的类型
        """
        return [
            IndustryType.AGRICULTURAL_FAH_FISHERY,
            IndustryType.MINING_INDUSTRY,
            IndustryType.MANUFACTURING,
            IndustryType.WATER_ELECTRICITY_GAS,
            IndustryType.CONSTRUCTION_INDUSTRY,
            IndustryType.WHOLESALE_RETAIL,
            IndustryType.TRANSPORTATION_STORAGE,
            IndustryType.ACCOMMODATION,
            IndustryType.INFORMATION_TECHNOLOGY,
            IndustryType.FINANCIAL_INDUSTRY,
            IndustryType.REAL_ESTATE_INDUSTRY,
            IndustryType.BUSINESS_SERVICES,
            IndustryType.RESEARCH_SERVICE,
            IndustryType.PUBLIC_ENVIRONMENTAL_PROTECTION,
            IndustryType.RESIDENT_SERVICE,
            IndustryType.EDUCATION_INDUSTRY,
            IndustryType.HEALTH_INDUSTRY,
            IndustryType.CULTURAL_COMMUNICATION,
            IndustryType.COMPREHENSIVE,
        ]

    # 农业、林业、牧业、渔业
    AGRICULTURAL_FAH_FISHERY = (1, ["农林牧渔", "农、林、牧、渔业"])
    # 采矿业
    MINING_INDUSTRY = (2, ["采矿业"])
    # 制造业
    MANUFACTURING = (3, ["制造业"])
    # 水电煤气
    WATER_ELECTRICITY_GAS = (4, ["水电煤气", "电力、热力、燃气及水生产和供应业"])
    # 建筑业
    CONSTRUCTION_INDUSTRY = (5, ["建筑业"])
    # 批发零售
    WHOLESALE_RETAIL = (6, ["批发零售", "批发和零售业"])
    # 运输仓储
    TRANSPORTATION_STORAGE = (7, ["运输仓储", "交通运输、仓储和邮政业"])
    # 住宿餐饮
    ACCOMMODATION = (8, ["住宿餐饮", "住宿和餐饮业"])
    # 信息技术
    INFORMATION_TECHNOLOGY = (9, ["信息技术", "信息传输、软件和信息技术服务业"])
    # 金融业
    FINANCIAL_INDUSTRY = (10, ["金融业"])
    # 房地产
    REAL_ESTATE_INDUSTRY = (11, ["房地产", "房地产业"])
    # 商务服务
    BUSINESS_SERVICES = (12, ["商务服务", "租赁和商务服务业"])
    # 科研服务
    RESEARCH_SERVICE = (13, ["科研服务", "科学研究和技术服务业"])
    # 公共环保
    PUBLIC_ENVIRONMENTAL_PROTECTION = (14, ["公共环保", "水利、环境和公共设施管理业"])
    # 居民服务
    RESIDENT_SERVICE = (15, ["居民服务", "居民服务、修理和其他服务业"])
    # 教育
    EDUCATION_INDUSTRY = (16, ["教育"])
    # 卫生
    HEALTH_INDUSTRY = (17, ["卫生", "卫生和社会工作"])
    # 文化传播
    CULTURAL_COMMUNICATION = (18, ["文化传播", "文化、体育和娱乐业"])
    # 综合
    COMPREHENSIVE = (19, ["综合"])
