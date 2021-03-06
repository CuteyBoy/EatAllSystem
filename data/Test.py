import re
import os
import requests
from data.remote.download.StockDownload import StockCodeAllDownload
from data.remote.download.StockFrDownload import StockFrDownload
from data.database.table.StockFrTable import StockFrTable


def download_stock_code():
    code_download = StockCodeAllDownload()
    code_download.download_to_db()


def download_fr_data():
    fr_download = StockFrDownload()
    # fr_download.filter()
    fr_download.download_to_db()


# download_stock_code()
# download_fr_data()

#
# frTable = StockFrTable()
# data_list = frTable.find().limit(2)
# all_size = data_list.count()
# print("size=", all_size)
# for fr in data_list:
#     print(fr)
# if data_list.count() > 0:
#     for fr in data_list:
#         code = fr["code"]
#         title = str(fr["title"])
#         year = title.split("：")[-1].split("年")[0]
#         path_url = str(fr["pdf_path"])
#         suffix_name = path_url.split("/")[-1]
#         save_dir = "stock%s" % code
#         save_stock_dir = os.path.join(os.getcwd(), save_dir)
#         file_path_name = "%s/_%s_%s" % (save_dir, year, suffix_name)
#         save_file_path = os.path.join(os.getcwd(), file_path_name)
#         if os.path.exists(save_stock_dir) is False:
#             os.mkdir(save_stock_dir)
#         with open(save_file_path, 'wb') as stock_file:
#             with requests.get(path_url, stream=True) as pdf:
#                 stock_file.write(pdf.content)

content = """流动资产：     
    货币资金 
 
 
    结算备付金     
    拆出资金     
    交易性金融资产     
    以公允价值计量且其变动计入
   
当期损益的金融资产 
    衍生金融资产     
年年度报告全文 
    应收票据     
    应收账款 
 
 
    应收款项融资     
    预付款项 
 
 
    应收保费     
    应收分保账款     
    应收分保合同准备金     
    其他应收款 
 
 
      其中：应收利息     
            应收股利     
    买入返售金融资产     
    存货 
 
 
    合同资产     
    持有待售资产     
    一年内到期的非流动资产     
    其他流动资产 
 
 
流动资产合计 
 
 
非流动资产：     
    发放贷款和垫款     
    债权投资     
    可供出售金融资产   
 
    其他债权投资     
    持有至到期投资     
    长期应收款     
    长期股权投资 
 
 
    其他权益工具投资 
   
    其他非流动金融资产     
    投资性房地产 
 
 
    固定资产 
 
 
    在建工程 
 
 
    生产性生物资产     
    油气资产     
    使用权资产     
    无形资产 
 
 
年年度报告全文 
    开发支出     
    商誉     
    长期待摊费用 
 
 
    递延所得税资产 
 
 
    其他非流动资产 
 
 
非流动资产合计 
 
 
资产总计 
 
 
流动负债：     
    短期借款 
 
 
    向中央银行借款     
    拆入资金     
    交易性金融负债     
    以公允价值计量且其变动计入
   
当期损益的金融负债 
    衍生金融负债     
    应付票据 
 
 
    应付账款 
 
 
    预收款项 
 
 
    合同负债     
    卖出回购金融资产款     
    吸收存款及同业存放     
    代理买卖证券款     
    代理承销证券款     
    应付职工薪酬 
 
 
    应交税费 
 
 
    其他应付款 
 
 
      其中：应付利息   
 
            应付股利     
    应付手续费及佣金     
    应付分保账款     
    持有待售负债     
    一年内到期的非流动负债 
 
 
    其他流动负债     
流动负债合计 
 
 
年年度报告全文 
非流动负债：     
    保险合同准备金     
    长期借款 
 
 
    应付债券 
 
 
      其中：优先股     
            永续债     
    租赁负债     
    长期应付款 
 
 
    长期应付职工薪酬     
    预计负债   
 
    递延收益 
 
 
    递延所得税负债 
 
 
    其他非流动负债     
非流动负债合计 
 
 
负债合计 
 
 
所有者权益：     
    股本 
 
 
    其他权益工具     
      其中：优先股     
            永续债     
    资本公积 
 
 
    减：库存股     
    其他综合收益     
    专项储备     
    盈余公积 
 
 
    一般风险准备     
    未分配利润 
 
 
归属于母公司所有者权益合计 
 
 
    少数股东权益 
 
 
所有者权益合计 
 
 
负债和所有者权益总计 
 
 
法定代表人：蒋利亚                     主管会计工作负责人：颜梦玉                     会计机构负责人：邱君 
年年度报告全文 
            永续债     
    租赁负债     
    长期应付款 
 
 
    长期应付职工薪酬     
    预计负债     
    递延收益     
    递延所得税负债     
    其他非流动负债     
非流动负债合计 
 
 
负债合计 
 
 
所有者权益：     
    股本 
 
 
    其他权益工具     
      其中：优先股     
            永续债     
    资本公积 
 
 
    减：库存股     
    其他综合收益     
    专项储备     
    盈余公积 
 
 
    未分配利润 
 
 
所有者权益合计 
 
 
负债和所有者权益总计 
 
 
、合并利润表 
单位：元 
项目 
年度 
年度 
一、营业总收入 
 
 
    其中：营业收入 
 
 
          利息收入     
          已赚保费     
          手续费及佣金收入     
二、营业总成本 
 
 
    其中：营业成本 
 
 
年年度报告全文 
          利息支出     
          手续费及佣金支出     
          退保金     
          赔付支出净额     
          提取保险责任合同准备
   
金净额 
          保单红利支出     
          分保费用     
          税金及附加 
 
 
          销售费用 
 
 
          管理费用 
 
 
          研发费用     
          财务费用 
 
 
            其中：利息费用 
 
 
                  利息收入 
 
 
    加：其他收益 
 
 
        投资收益（损失以“－”号
 
 
填列） 
        其中：对联营企业和合营企
 
 
业的投资收益 
            以摊余成本计量的金
   
融资产终止确认收益 
        汇兑收益（损失以“-”号填
   
列） 
        净敞口套期收益（损失以
   
“－”号填列） 
        公允价值变动收益（损失以
   
“－”号填列） 
        信用减值损失（损失以“-”
   
号填列） 
        资产减值损失（损失以“-”
 
 
号填列） 
        资产处置收益（损失以“-”
 
 
号填列） 
三、营业利润（亏损以“－”号填列） 
 
 
    加：营业外收入 
 
 
年年度报告全文 
    减：营业外支出 
 
 
四、利润总额（亏损总额以“－”号
 
 
填列） 
    减：所得税费用 
 
 
五、净利润（净亏损以“－”号填列） 
 
 
  （一）按经营持续性分类     
   
.持续经营净利润（净亏损以
 
 
“－”号填列） 
   
.终止经营净利润（净亏损以
   
“－”号填列） 
  （二）按所有权归属分类     
   
.归属于母公司所有者的净利润 
 
 
   
.少数股东损益 
 
 
六、其他综合收益的税后净额     
  归属母公司所有者的其他综合收
   
益的税后净额 
    （一）不能重分类进损益的其他
   
综合收益 
         
.重新计量设定受益计划
   
变动额 
         
.权益法下不能转损益的
   
其他综合收益 
         
.其他权益工具投资公允
   
价值变动 
         
.企业自身信用风险公允
   
价值变动 
         
.其他     
    （二）将重分类进损益的其他综
   
合收益 
         
.权益法下可转损益的其
   
他综合收益 
         
.其他债权投资公允价值
   
变动 
         
.可供出售金融资产公允
   
价值变动损益 
         
.金融资产重分类计入其
   
他综合收益的金额 
年年度报告全文 
         
.持有至到期投资重分类
   
为可供出售金融资产损益 
         
.其他债权投资信用减值
   
准备 
         
.现金流量套期储备     
         
.外币财务报表折算差额     
         
.其他     
  归属于少数股东的其他综合收益
   
的税后净额 
七、综合收益总额 
 
 
    归属于母公司所有者的综合收
 
 
益总额 
    归属于少数股东的综合收益总
 
 
额 
八、每股收益：     
    （一）基本每股收益 
 
 
    （二）稀释每股收益 
 
 
本期发生同一控制下企业合并的，被合并方在合并前实现的净利润为：元，上期被合并方实现的净利润为：元。 
法定代表人：蒋利亚                     主管会计工作负责人：颜梦玉                     会计机构负责人：邱君 
、母公司利润表 
单位：元 
项目 
年度 
年度 
一、营业收入 
 
 
    减：营业成本 
 
 
        税金及附加 
 
 
        销售费用 
 
 
        管理费用 
 
 
        研发费用     
        财务费用 
 
 
          其中：利息费用 
 
 
                利息收入 
 
 
    加：其他收益 
 
 
        投资收益（损失以“－”
 
 
号填列） 
年年度报告全文 
六、期末现金及现金等价物余额 
 
 
、母公司现金流量表 
单位：元 
项目 
年度 
年度 
一、经营活动产生的现金流量：     
    销售商品、提供劳务收到的现
 
 
金 
    收到的税费返还     
    收到其他与经营活动有关的现
 
 
金 
经营活动现金流入小计 
 
 
    购买商品、接受劳务支付的现
 
 
金 
    支付给职工以及为职工支付的
 
 
现金 
    支付的各项税费 
 
 
    支付其他与经营活动有关的现
 
 
金 
经营活动现金流出小计 
 
 
经营活动产生的现金流量净额 
 
 
二、投资活动产生的现金流量：     
    收回投资收到的现金   
 
    取得投资收益收到的现金     
    处置固定资产、无形资产和其
 
 
他长期资产收回的现金净额 
    处置子公司及其他营业单位收
   
到的现金净额 
    收到其他与投资活动有关的现
 
 
金 
投资活动现金流入小计 
 
 
    购建固定资产、无形资产和其
 
 
他长期资产支付的现金 
    投资支付的现金     
    取得子公司及其他营业单位支
   
付的现金净额 
年年度报告全文 
    支付其他与投资活动有关的现
 
 
金 
投资活动现金流出小计 
 
 
投资活动产生的现金流量净额 
 
 
三、筹资活动产生的现金流量：     
    吸收投资收到的现金     
    取得借款收到的现金 
 
 
    收到其他与筹资活动有关的现
 
 
金 
筹资活动现金流入小计 
 
 
    偿还债务支付的现金 
 
 
    分配股利、利润或偿付利息支
 
 
付的现金 
    支付其他与筹资活动有关的现
 
 
金 
筹资活动现金流出小计 
 
 
筹资活动产生的现金流量净额 
 
 
四、汇率变动对现金及现金等价物
   
的影响 
五、现金及现金等价物净增加额 
 
 
    加：期初现金及现金等价物余
 
 
额 
六、期末现金及现金等价物余额 
 
 
、合并所有者权益变动表 
本期金额 
单位：元 
年度 
归属于母公司所有者权益 
所有
其他权益工具  少数
项目  减： 其他 一般 未分 者权
股 优 永 资本 专项 盈余 股东
其 库存 综合 风险 配利 其他  小计  益合
本  先 续 公积  储备  公积  权益 
他  股  收益  准备  润  计 
股  债 
"""

result_list = content.replace("\n", "").split()
for result in result_list:
    print(result.replace(" ", ""))
