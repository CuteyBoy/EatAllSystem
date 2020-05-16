from app.src.data.database.table.AbsTable import AbsTable, TableFields

# 用于存储股票对应的财报数据
STOCK_FR_TABLE = "stock_financial_report"


@TableFields(
    # 股票代码字段
    code=str,
    # 财报标题字段
    title=str,
    # 财报网络地址字段
    pdf_path=str,
    # 财报pdf文件大小字段
    pdf_size=float,
    # 财报保存在本地路径字段
    local_pdf_path=str
)
class StockFrTable(AbsTable):
    """
    用于存放股票对应的财报数据的表
    """
    def __init__(self):
        super().__init__(STOCK_FR_TABLE)
