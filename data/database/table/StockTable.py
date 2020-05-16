from data.database.table.AbsTable import AbsTable, TableFields

# 用于存放所有上市公司的股票信息
STOCK_TABLE = "stock_table"


@TableFields(
    # 所在交易所类型字段
    exchange_type=str,
    # 股票代码字段
    stock_code=str,
    # 股票名字字段
    stock_name=str,
    # 上市时间字段
    market_time=str,
    # 所属行业字段
    industry_type=int,
    # 所属行业名字段
    industry_name=str,
    # A股总股本字段
    a_total_stock=int,
    # A股流通股本字段
    a_trade_stock=int,
    # 公司所在城市字段
    city=str,
    # 公司官网地址
    company_website=str
)
class StockTable(AbsTable):
    """
        用于保存所有股票的代码的表
        表字段明如下：
        stock_all: {
            type: 股票类型，表示是深交所(sz)还是上交所(sh)
            code: 股票代码,
            name: 上市公司名字，
            industry_type: 所属行业类型
            start_time: 上市时间
        }
        """
    def __int__(self):
        super().__init__(STOCK_TABLE)
