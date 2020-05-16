from data.database.table.AbsTable import AbsTable, TableFields

# 行业对应的每一项列表
INDUSTRY_PROJECT_TABLE = "industry_project_table"


@TableFields(
    exchange_type=str,
    industry_type=int,
    project_type=int,
    project_name=str
)
class IndustryProjectTable(AbsTable):
    """
    用于存放每个行业对应的财报每一项列表
    """

    def __init__(self):
        super().__init__(INDUSTRY_PROJECT_TABLE)
