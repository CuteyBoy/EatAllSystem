from data.database.table.AbsTable import AbsTable,TableFields

# 行业类型表
INDUSTRY_TABLE = "industry_table"


@TableFields(
    # 交易所类型
    exchange_type=str,
    # 行业类型
    industry_type=int,
    # 行业类型名
    industry_name=str
)
class IndustryTable(AbsTable):
    """
    用于存储股票所属的行业类型
    """

    def __init__(self):
        super().__init__(INDUSTRY_TABLE)
