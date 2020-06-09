from app.src.data.database.table.AbsTable import AbsTable, TableFields

# 行业对应的每一项列表
INDUSTRY_PROJECT_TABLE = "industry_project_table"


@TableFields(
    # 交易所类型
    exchange_type=str,
    # 行业类型
    industry_type=int,
    # 表类型字段（负债表、利润表、现金流量表）
    table_type=int,
    # 项目类型
    project_type=int,
    # 项目名
    project_name=str
)
class IndustryProjectTable(AbsTable):
    """
    用于存放每个行业对应的财报每一项列表
    """

    def __init__(self):
        super().__init__(INDUSTRY_PROJECT_TABLE)
