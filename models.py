# from __future__ import annotations

from sqlalchemy import Column, Integer, Float, String
from database import Base
from sqlalchemy import Column, String, Float, BigInteger, Text
from typing import Optional
class StockSummary(Base):
    __tablename__ = "stock_summary"

    id = Column(Integer, primary_key=True, index=True)
    名称 = Column(String(20), nullable=False)
    流通股本 = Column(Float, nullable=True)
    总市值 = Column(Float, nullable=True)
    平均市盈率 = Column(Float, nullable=True)
    上市公司 = Column(Integer, nullable=True)
    上市股票 = Column(Integer, nullable=True)
    流通市值 = Column(Float, nullable=True)
    报告时间 = Column(Integer, nullable=True)
    总股本 = Column(Float, nullable=True)




# Base = declarative_base()

class StockTotal(Base):
    __tablename__ = "stock_total"

    Date = Column(Text, primary_key=True)
    Code = Column(BigInteger, primary_key=True)
    Open = Column(Float)
    High = Column(Float)
    Low = Column(Float)
    Close = Column(Float)
    AdjClose = Column("Adj Close", Float)
    Volume = Column(Float)
    Amount = Column(Float)
    SwitchRate = Column(Float)
    SwitchAmount = Column(Float)
    ChangeRate = Column(Float)
    StockName = Column(Text)

class PublicSentiment(Base):
    __tablename__ = "微博舆情"
    name = Column(String(255), primary_key=True)  # 修改为 String(255)
    rate = Column(Float)


class SectorInfo(Base):
    __tablename__ = "行业成交数据"

    id = Column(BigInteger, primary_key=True)
    name = Column(Text)
    name_en = Column(Text)
    trading_days = Column(BigInteger)
    turnover_amount = Column(BigInteger)
    turnover_ratio = Column(Float)
    shares_traded = Column(BigInteger)
    shares_ratio = Column(Float)
    transactions = Column(BigInteger)
    transactions_ratio = Column(Float)


from sqlalchemy import Column, String, DateTime, func, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LiveAnalysis(Base):
    __tablename__ = "live_analysis"

    id = Column(BigInteger, primary_key=True, index=True, comment="主键ID")
    stock = Column(String(50), nullable=False, comment="股票名称")
    event_type = Column(String(50), nullable=False, comment="事件类型")
    timestamp = Column(DateTime, nullable=False, comment="事件发生时间")
    event = Column(String(100), nullable=True, comment="事件描述")
    created_at = Column(DateTime, server_default=func.now(), comment="记录创建时间")


from pydantic import BaseModel
from datetime import datetime

class LiveAnalysisBase(BaseModel):
    stock: str
    event_type: str
    timestamp: datetime
    event: Optional[str] = None

class LiveAnalysisCreate(LiveAnalysisBase):
    pass

class LiveAnalysisOut(LiveAnalysisBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class SectorDataIn(BaseModel):
    日期: str
    开盘价: Optional[float]
    最高价: Optional[float]
    最低价: Optional[float]
    收盘价: Optional[float]
    成交量: Optional[int]
    成交额: Optional[float]

class SectorDataOut(SectorDataIn):
    pass


Base_EVENT = declarative_base()
class Event(Base_EVENT):
    __tablename__ = "事件"

    序号 = Column(BigInteger, primary_key=True, index=True, nullable=True)  # 假设序号是主键
    代码 = Column(BigInteger, nullable=True)
    简称 = Column(Text, nullable=True)
    事件类型 = Column(Text, nullable=True)
    具体事项 = Column(Text, nullable=True)
    交易日 = Column(Text, nullable=True)

# Pydantic 模型定义，用于请求和响应校验
class EventBase(BaseModel):
    代码: Optional[int] = None
    简称: Optional[str] = None
    事件类型: Optional[str] = None
    具体事项: Optional[str] = None
    交易日: Optional[str] = None
class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class EventOut(EventBase):
    序号: int

    class Config:
        orm_mode = True


from typing import Optional
from pydantic import BaseModel



class BalanceSheetItem(BaseModel):
    报告日: Optional[str] = None
    流动资产: Optional[str] = None
    货币资金: Optional[str] = None
    结算备付金: Optional[str] = None
    拆出资金: Optional[str] = None
    交易性金融资产: Optional[str] = None
    买入返售金融资产: Optional[str] = None
    衍生金融资产: Optional[str] = None
    应收票据及应收账款: Optional[str] = None
    应收票据: Optional[str] = None
    应收账款: Optional[str] = None
    应收款项融资: Optional[str] = None
    预付款项: Optional[str] = None
    应收股利: Optional[str] = None
    应收利息: Optional[str] = None
    应收保费: Optional[str] = None
    应收分保账款: Optional[str] = None
    应收分保合同准备金: Optional[str] = None
    应收出口退税: Optional[str] = None
    应收补贴款: Optional[str] = None
    应收保证金: Optional[str] = None
    内部应收款: Optional[str] = None
    其他应收款: Optional[str] = None
    其他应收款_合计: Optional[str] = None
    存货: Optional[str] = None
    划分为持有待售的资产: Optional[str] = None
    待摊费用: Optional[str] = None
    待处理流动资产损益: Optional[str] = None
    一年内到期的非流动资产: Optional[str] = None
    其他流动资产: Optional[str] = None
    流动资产合计: Optional[str] = None
    非流动资产: Optional[str] = None
    发放贷款及垫款: Optional[str] = None
    债权投资: Optional[str] = None
    其他债权投资: Optional[str] = None
    以公允价值计量且其变动计入其他综合收益的金融资产: Optional[str] = None
    以摊余成本计量的金融资产: Optional[str] = None
    可供出售金融资产: Optional[str] = None
    长期股权投资: Optional[str] = None
    投资性房地产: Optional[str] = None
    长期应收款: Optional[str] = None
    其他权益工具投资: Optional[str] = None
    其他非流动金融资产: Optional[str] = None
    其他长期投资: Optional[str] = None
    固定资产原值: Optional[str] = None
    累计折旧: Optional[str] = None
    固定资产净值: Optional[str] = None
    固定资产减值准备: Optional[str] = None
    在建工程合计: Optional[str] = None
    在建工程: Optional[str] = None
    工程物资: Optional[str] = None
    固定资产净额: Optional[str] = None
    固定资产清理: Optional[str] = None
    固定资产及清理合计: Optional[str] = None
    生产性生物资产: Optional[str] = None
    公益性生物资产: Optional[str] = None
    油气资产: Optional[str] = None
    合同资产: Optional[str] = None
    使用权资产: Optional[str] = None
    无形资产: Optional[str] = None
    开发支出: Optional[str] = None
    商誉: Optional[str] = None
    长期待摊费用: Optional[str] = None
    股权分置流通权: Optional[str] = None
    递延所得税资产: Optional[str] = None
    其他非流动资产: Optional[str] = None
    非流动资产合计: Optional[str] = None
    资产总计: Optional[str] = None
    流动负债: Optional[str] = None
    短期借款: Optional[str] = None
    向中央银行借款: Optional[str] = None
    吸收存款及同业存放: Optional[str] = None
    拆入资金: Optional[str] = None
    交易性金融负债: Optional[str] = None
    衍生金融负债: Optional[str] = None
    应付票据及应付账款: Optional[str] = None
    应付票据: Optional[str] = None
    应付账款: Optional[str] = None
    预收款项: Optional[str] = None
    合同负债: Optional[str] = None
    卖出回购金融资产款: Optional[str] = None
    应付手续费及佣金: Optional[str] = None
    应付职工薪酬: Optional[str] = None
    应交税费: Optional[str] = None
    应付利息: Optional[str] = None
    应付股利: Optional[str] = None
    应付保证金: Optional[str] = None
    内部应付款: Optional[str] = None
    其他应付款: Optional[str] = None
    其他应付款合计: Optional[str] = None
    其他应交款: Optional[str] = None
    担保责任赔偿准备金: Optional[str] = None
    应付分保账款: Optional[str] = None
    保险合同准备金: Optional[str] = None
    代理买卖证券款: Optional[str] = None
    代理承销证券款: Optional[str] = None
    国际票证结算: Optional[str] = None
    国内票证结算: Optional[str] = None
    预提费用: Optional[str] = None
    预计流动负债: Optional[str] = None
    应付短期债券: Optional[str] = None
    划分为持有待售的负债: Optional[str] = None
    一年内的递延收益: Optional[str] = None
    一年内到期的非流动负债: Optional[str] = None
    其他流动负债: Optional[str] = None
    流动负债合计: Optional[str] = None
    非流动负债: Optional[str] = None
    长期借款: Optional[str] = None
    应付债券: Optional[str] = None
    应付债券_优先股: Optional[str] = None
    应付债券_永续债: Optional[str] = None
    租赁负债: Optional[str] = None
    长期应付职工薪酬: Optional[str] = None
    长期应付款: Optional[str] = None
    长期应付款合计: Optional[str] = None
    专项应付款: Optional[str] = None
    预计非流动负债: Optional[str] = None
    长期递延收益: Optional[str] = None
    递延所得税负债: Optional[str] = None
    其他非流动负债: Optional[str] = None
    非流动负债合计: Optional[str] = None
    负债合计: Optional[str] = None
    所有者权益: Optional[str] = None
    实收资本_或股本: Optional[str] = None
    其他权益工具: Optional[str] = None
    优先股: Optional[str] = None
    永续债: Optional[str] = None
    资本公积: Optional[str] = None
    减_库存股: Optional[str] = None
    其他综合收益: Optional[str] = None
    专项储备: Optional[str] = None
    盈余公积: Optional[str] = None
    一般风险准备: Optional[str] = None
    未确定的投资损失: Optional[str] = None
    未分配利润: Optional[str] = None
    拟分配现金股利: Optional[str] = None
    外币报表折算差额: Optional[str] = None
    归属于母公司股东权益合计: Optional[str] = None
    少数股东权益: Optional[str] = None
    所有者权益_或股东权益_合计: Optional[str] = None
    负债和所有者权益_或股东权益_总计: Optional[str] = None
    数据源: Optional[str] = None
    是否审计: Optional[str] = None
    公告日期: Optional[str] = None
    币种: Optional[str] = None
    类型: Optional[str] = None
    更新日期: Optional[str] = None

class BalanceSheetCreate(BalanceSheetItem):
    pass
