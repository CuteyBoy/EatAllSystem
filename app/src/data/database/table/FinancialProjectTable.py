from app.src.data.database.table.AbsTable import AbsTable, TableFields

# 财务报表（合并负债表、合并利润表、合并现金流量表）里的各项参数表
FINANCIAL_PROJECT_TABLE = "financial_project_table"


@TableFields(
    # 股票代码字段
    code=str,
    # 股票上市交易所字段（sz,sh）
    stock_exchange=str,
    # 股票名字段
    stock_name=str,
    # 股票所属类型字段
    industry_type=int,
    # 表类型字段（负债表、利润表、现金流量表）
    table_type=int,
    # 表类名字段
    table_name=str,
    # 财报中的项目类型字段
    project_type=int,
    # 财报中的项目名字段
    project_name=str,
    # 期末余额字段
    ending_balance=float,
    # 期初余额字段
    opening_balance=float,
    # 项目所属年份字段
    table_year=str,
    # 表周所属财报周期字段（一季度，二季度、半年报、三季度，年报）
    table_period=int,
    # 表周期名字段
    table_period_name=str,
    # 预留字段
    reserved=object
)
class FinancialProjectTable(AbsTable):
    """
    该表主要存放财务报表（合并负债表、合并利润表、合并现金流量表）
    里面的各项参数，方便后面进行统计计算
    """
    def __int__(self):
        super().__init__(FINANCIAL_PROJECT_TABLE)
