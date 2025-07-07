# 数据库连接配置
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:34793479@192.168.5.2:3306/stock_data"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


PUBLIC_SENTIMENT_DATABASE_URL = "mysql+pymysql://root:34793479@192.168.5.2:3306/public_sentiment"

engine2 = create_engine(PUBLIC_SENTIMENT_DATABASE_URL)
SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)

def get_sentiment_db():
    db = SessionLocal2()
    try:
        yield db
    finally:
        db.close()

PUBLIC_SECTOR_DATABASE_URL = "mysql+pymysql://root:34793479@192.168.5.2:3306/sector"

engine3 = create_engine(PUBLIC_SECTOR_DATABASE_URL)
SessionLocal3 = sessionmaker(autocommit=False, autoflush=False, bind=engine3)

def get_sector_db():
    db = SessionLocal3()
    try:
        yield db
    finally:
        db.close()

ANALYSIS_REPORT_DATABASE_URL = "mysql+pymysql://root:34793479@192.168.5.2:3306/report"

engine4 = create_engine(ANALYSIS_REPORT_DATABASE_URL)
SessionLocal4 = sessionmaker(autocommit=False, autoflush=False, bind=engine4)

def get_analysis_db():
    db = SessionLocal4()
    try:
        yield db
    finally:
        db.close()

SECTOR_DATA_DATABASE_URL = "mysql+pymysql://root:34793479@192.168.5.2:3306/sector_data"

engine5 = create_engine(SECTOR_DATA_DATABASE_URL)
SessionLocal5 = sessionmaker(autocommit=False, autoflush=False, bind=engine5)

def get_sector_data_db():
    db = SessionLocal5()
    try:
        yield db
    finally:
        db.close()


SECTOR_STOCK_INFO_URL = "mysql+pymysql://root:34793479@192.168.5.2:3306/stock_info"
engine6 = create_engine(SECTOR_STOCK_INFO_URL)

SessionLocal6 = sessionmaker(autocommit=False, autoflush=False, bind=engine6)

def get_stock_info_db():
    db = SessionLocal6()
    try:
        yield db
    finally:
        db.close()


# ====================
# 事件的数据库
SECTOR_EVENT_URL = "mysql+pymysql://root:34793479@192.168.5.2:3306/event"
engine_event = create_engine(SECTOR_EVENT_URL)

SessionLocal_EVENT = sessionmaker(autocommit=False, autoflush=False, bind=engine_event)

def get_event_db():
    db = SessionLocal_EVENT()
    try:
        yield db
    finally:
        db.close()

# ====================
# 资产负债的数据库
SECTOR_FINANCIAL_BALANCE_URL = "mysql+pymysql://root:34793479@192.168.5.2:3306/financial_balance"
engine_financial_balance = create_engine(SECTOR_FINANCIAL_BALANCE_URL)

SessionLocal_FINANCIAL_BALANCE = sessionmaker(autocommit=False, autoflush=False, bind=engine_financial_balance)

def get_financial_balance_db():
    db = SessionLocal_FINANCIAL_BALANCE()
    try:
        yield db
    finally:
        db.close()

# ====================
# 现金流量表的数据库
SECTOR_FINANCIAL_CASHFLOW_URL = "mysql+pymysql://root:34793479@192.168.5.2:3306/financial_cashflow"
engine_financial_cashflow = create_engine(SECTOR_FINANCIAL_CASHFLOW_URL)

SessionLocal_FINANCIAL_CASHFLOW = sessionmaker(autocommit=False, autoflush=False, bind=engine_financial_cashflow)

def get_financial_cashflow_db():
    db = SessionLocal_FINANCIAL_CASHFLOW()
    try:
        yield db
    finally:
        db.close()


# ====================
# 现金流量表的数据库
SECTOR_FINANCIAL_PROFIT_URL = "mysql+pymysql://root:34793479@192.168.5.2:3306/financial_profit"
engine_financial_profit = create_engine(SECTOR_FINANCIAL_PROFIT_URL)

SessionLocal_FINANCIAL_PROFIT = sessionmaker(autocommit=False, autoflush=False, bind=engine_financial_profit)

def get_financial_profit_db():
    db = SessionLocal_FINANCIAL_PROFIT()
    try:
        yield db
    finally:
        db.close()