from http.client import HTTPException
from sqlite3 import IntegrityError
from turtle import update
from typing import List, Optional, Dict
from fastapi import  Depends
from numpy import delete, insert
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import schemas
from starlette.responses import JSONResponse

import models
from models import Base, StockSummary, StockTotal, LiveAnalysisOut, LiveAnalysisCreate, SectorDataOut, SectorDataIn, \
    Event, EventOut, EventCreate, EventUpdate, BalanceSheetItem
from models import PublicSentiment
from models import LiveAnalysis
from database import SessionLocal, engine, get_sector_data_db, engine5, get_stock_info_db, get_event_db, \
    get_financial_balance_db, get_financial_cashflow_db, get_financial_profit_db
from database import get_sentiment_db  #获取数据库会话
from database import get_db
from database import get_sector_db
from database import get_analysis_db
from datetime import datetime
from models import SectorInfo
from sqlalchemy import text, func
from sqlalchemy import desc
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query
from utils import get_sector_table
# 根据股票名获取资产负债表数据
from sqlalchemy import MetaData, Table
from sqlalchemy.orm import sessionmaker
app = FastAPI()

# CORS：允许前端访问 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.5.4:8080"],  # 允许的前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)


# # 获取所有资产负债表表名（股票名）
# @app.get("/api/financial-balance/tables/", response_model=list[str])
# def get_all_tables(db: Session = Depends(get_financial_balance_db)):
#     """获取数据库中所有财务资产负债表的表名（股票名）"""
#     # 获取数据库连接
#     connection = db.connection()
#
#     # 根据不同数据库类型执行相应的查询
#     if connection.dialect.name == 'sqlite':
#         # SQLite 查询
#         result = connection.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     elif connection.dialect.name == 'postgresql':
#         # PostgreSQL 查询
#         result = connection.execute("""
#             SELECT table_name
#             FROM information_schema.tables
#             WHERE table_schema = 'public';
#         """)
#     elif connection.dialect.name == 'mysql':
#         # MySQL 查询
#         result = connection.execute("SHOW TABLES;")
#     else:
#         raise HTTPException(status_code=501, detail="不支持的数据库类型")
#
#     # 提取表名列表
#     tables = [row[0] for row in result.fetchall()]
#
#     # 过滤掉系统表（如果需要）
#     # 这里假设你的表名都是股票名，没有特殊的系统表前缀
#     # 如果有，可以添加过滤逻辑，如：tables = [t for t in tables if not t.startswith('sys_')]
#
#     return tables


# 读取指定表名的全部财务资产负债表记录
# @app.get("/api/financial-balance/{table_name}", response_model=List[schemas.BalanceSheetItem])
# def read_financial_balance_table(
#         table_name: str,
#         db: Session = Depends(get_financial_balance_db),
#         skip: int = 0,
#         limit: int = 100
# ):
#     # 动态创建指定表的模型
#     metadata = MetaData()
#     dynamic_table = Table(
#         table_name,
#         metadata,
#         autoload_with=db.get_bind()  # 自动加载表结构
#     )
#
#     # 检查表格是否存在
#     if not db.get_bind().has_table(table_name):
#         raise HTTPException(status_code=400, detail=f"表 '{table_name}' 不存在")
#
#     # 执行查询
#     query = db.query(dynamic_table).offset(skip).limit(limit)
#     results = query.all()
#
#     # 将结果转换为字典列表（适配 Pydantic 模型）
#     records = []
#     for row in results:
#         record = dict(row._mapping)  # SQLAlchemy 2.0+ 访问方式
#         records.append(record)
#
#     return records



# A股列表(Stock_info表)
@app.get("/api/a-stock-list", response_class=JSONResponse)
def get_a_stock_list(
    keyword: str = Query(..., description="搜索关键词（股票名称或代码）"),
    db: Session = Depends(get_stock_info_db)
):
    try:
        sql = text("""
            SELECT DISTINCT name, code
            FROM `A股列表`
            WHERE name LIKE :kw OR CAST(code AS CHAR) LIKE :kw
            LIMIT 20
        """)
        like_keyword = f"%{keyword}%"
        result = db.execute(sql, {"kw": like_keyword}).fetchall()

        stocks = [
            {"label": f"{row.name}（{row.code}）", "value": row.name}
            for row in result if row.name and row.code
        ]

        return stocks

    except Exception as e:
        print("🔴 查询失败：", str(e))
        return JSONResponse(status_code=500, content={"error": "数据库查询失败"})

from database import get_financial_balance_db

# ------------------------------
# 查询指定表名的全部记录
# ------------------------------
# 分页模型（包含数据和总记录数）
class PaginationResponse(BaseModel):
    data: List[Dict]  # 当前页数据列表
    total: int  # 总记录数（前端分页跳转依赖这个字段）


# 利润表分页查询接口
@app.get("/api/profit/{table_name}", response_model=PaginationResponse)
def get_profit_items(
        table_name: str,
        db: Session = Depends(get_financial_profit_db),  # 使用利润表数据库连接
        skip: int = 0,
        limit: int = 100
):
    # 表名存在性校验
    if not db.bind.has_table(table_name):
        raise HTTPException(status_code=404, detail=f"表 '{table_name}' 不存在")

    # 动态加载表结构
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=db.bind)

    # 查询当前页数据
    current_page_data = db.query(table).offset(skip).limit(limit).all()
    if not current_page_data and skip != 0:
        raise HTTPException(status_code=404, detail="当前页无数据，请检查页码")

    # 计算总记录数
    total_count = db.query(table).count()

    return {
        "data": [dict(row._mapping) for row in current_page_data],
        "total": total_count
    }

# ------------------------------
# 查询指定股票的现金流量表数据

@app.get("/api/cashflow/{table_name}", response_model=PaginationResponse)
def get_cashflow_items(
        table_name: str,
        db: Session = Depends(get_financial_cashflow_db),  # 使用现金流量表的数据库连接
        skip: int = 0,  # 前端传入：(currentPage - 1) * pageSize
        limit: int = 100  # 前端传入：pageSize
):
    # 安全检查：验证表名是否存在（防止SQL注入和非法表名）
    if not db.bind.has_table(table_name):
        raise HTTPException(status_code=404, detail=f"表 '{table_name}' 不存在")

    # 动态加载表结构
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=db.bind)

    # 1. 查询当前页数据
    current_page_data = db.query(table).offset(skip).limit(limit).all()
    if not current_page_data and skip != 0:
        # 如果当前页没数据且不是第一页，说明页码超出范围
        raise HTTPException(status_code=404, detail="当前页无数据，请检查页码")

    # 2. 查询总记录数（用于前端分页计算）
    total_count = db.query(table).count()

    # 3. 构造分页响应
    return {
        "data": [dict(row._mapping) for row in current_page_data],
        "total": total_count
    }




# 2. 完善分页查询接口
@app.get("/api/balance/{table_name}", response_model=PaginationResponse)
def get_balance_items(
        table_name: str,
        db: Session = Depends(get_financial_balance_db),
        skip: int = 0,  # 前端传入：(currentPage - 1) * pageSize
        limit: int = 100  # 前端传入：pageSize
):
    # 安全检查：验证表名是否存在（防止SQL注入和非法表名）
    if not db.bind.has_table(table_name):
        raise HTTPException(status_code=404, detail=f"表 '{table_name}' 不存在")

    # 动态加载表结构
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=db.bind)

    # 1. 查询当前页数据（已实现，保留）
    current_page_data = db.query(table).offset(skip).limit(limit).all()
    if not current_page_data and skip != 0:
        # 如果当前页没数据且不是第一页，说明页码超出范围
        raise HTTPException(status_code=404, detail="当前页无数据，请检查页码")

    # 2. 查询总记录数（新增：前端分页跳转依赖这个）
    total_count = db.query(table).count()  # 计算表中所有记录的总数

    # 3. 构造分页响应（数据+总记录数）
    return {
        "data": [dict(row._mapping) for row in current_page_data],  # 当前页数据
        "total": total_count  # 总记录数（关键）
    }


# ------------------------------
# 查询单条记录
# ------------------------------
@app.get("/api/balance/{table_name}/{report_date}", response_model=BalanceSheetItem)
def get_balance_item(table_name: str, report_date: str, db: Session = Depends(get_financial_balance_db)):
    sql = text(f"SELECT * FROM `{table_name}` WHERE 报告日 = :report_date LIMIT 1")
    result = db.execute(sql, {"report_date": report_date}).fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="记录未找到")
    return dict(result._mapping)

# ------------------------------
# 新增一条记录
# ------------------------------
@app.post("/api/balance/{table_name}", response_model=BalanceSheetItem)
def create_balance_item(table_name: str, item: BalanceSheetItem, db: Session = Depends(get_financial_balance_db)):
    columns = ', '.join([f"`{col}`" for col in item.dict().keys()])
    placeholders = ', '.join([f":{col}" for col in item.dict().keys()])
    sql = text(f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})")
    db.execute(sql, item.dict())
    db.commit()
    return item

# ------------------------------
# 更新一条记录
# ------------------------------
@app.put("/api/balance/{table_name}/{report_date}", response_model=BalanceSheetItem)
def update_balance_item(table_name: str, report_date: str, item: BalanceSheetItem, db: Session = Depends(get_financial_balance_db)):
    update_parts = ', '.join([f"`{col}` = :{col}" for col in item.dict().keys() if col != "报告日"])
    sql = text(f"""
        UPDATE `{table_name}`
        SET {update_parts}
        WHERE 报告日 = :report_date
    """)
    params = item.dict()
    params["report_date"] = report_date
    result = db.execute(sql, params)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="记录未找到")
    return item

# ------------------------------
# 删除一条记录
# ------------------------------
@app.delete("/api/balance/{table_name}/{report_date}")
def delete_balance_item(table_name: str, report_date: str, db: Session = Depends(get_financial_balance_db)):
    sql = text(f"DELETE FROM `{table_name}` WHERE 报告日 = :report_date")
    result = db.execute(sql, {"report_date": report_date})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="记录未找到")
    return {"message": f"已删除 报告日 = {report_date} 的记录"}


# 板块具体接口

@app.get("/api/sector/{table_name}", response_model=List[SectorDataOut])
def get_sector_data(
    table_name: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_sector_data_db)
):
    table = get_sector_table(table_name, engine5)

    # ✅ SQLAlchemy 1.2 兼容写法
    stmt = table.select()

    if start_date:
        stmt = stmt.where(table.c.日期 >= start_date)
    if end_date:
        stmt = stmt.where(table.c.日期 <= end_date)

    stmt = stmt.offset(skip).limit(limit)

    result = db.execute(stmt).fetchall()

    return [dict(row) for row in result]

@app.post("/api/sector/{table_name}")
def create_sector_data(
    table_name: str,
    data: SectorDataIn,
    db: Session = Depends(get_sector_data_db)
):
    table = get_sector_table(table_name, engine5)
    stmt = insert(table).values(**data.dict())
    db.execute(stmt)
    db.commit()
    return {"message": "数据插入成功"}

@app.put("/api/sector/{table_name}")
def update_sector_data(
    table_name: str,
    日期: str,
    data: SectorDataIn,
    db: Session = Depends(get_sector_data_db)
):
    table = get_sector_table(table_name, engine5)
    stmt = update(table).where(table.c.日期 == 日期).values(**data.dict())
    result = db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="未找到指定日期的数据")
    db.commit()
    return {"message": "数据更新成功"}

@app.delete("/api/sector/{table_name}")
def delete_sector_data(
    table_name: str,
    日期: str,
    db: Session = Depends(get_sector_data_db)
):
    table = get_sector_table(table_name, engine5)
    stmt = delete(table).where(table.c.日期 == 日期)
    result = db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="未找到指定日期的数据")
    db.commit()
    return {"message": "数据删除成功"}


# 异常分析相关接口
@app.get("/api/live-analysis", response_model=List[LiveAnalysisOut])
def get_live_analysis_list(
    stock: Optional[str] = Query(None, description="股票名称"),
    event_type: Optional[str] = Query(None, description="事件类型"),
    start_time: Optional[datetime] = Query(None, description="开始时间（格式: YYYY-MM-DDTHH:MM:SS）"),
    end_time: Optional[datetime] = Query(None, description="结束时间（格式: YYYY-MM-DDTHH:MM:SS）"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_analysis_db)
):
    query = db.query(LiveAnalysis)

    if stock:
        query = query.filter(LiveAnalysis.stock == stock)

    if event_type:
        query = query.filter(LiveAnalysis.event_type == event_type)

    if start_time:
        query = query.filter(LiveAnalysis.timestamp >= start_time)

    if end_time:
        query = query.filter(LiveAnalysis.timestamp <= end_time)

    query = query.order_by(LiveAnalysis.timestamp.desc())

    return query.offset(skip).limit(limit).all()

@app.get("/api/live-analysis/{id}", response_model=LiveAnalysisOut)
def get_live_analysis_by_id(id: int, db: Session = Depends(get_analysis_db)):
    record = db.query(LiveAnalysis).filter(LiveAnalysis.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录未找到")
    return record


@app.post("/api/live-analysis", response_model=LiveAnalysisOut)
def create_live_analysis(data: LiveAnalysisCreate, db: Session = Depends(get_analysis_db)):
    record = LiveAnalysis(**data.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.delete("/api/live-analysis/{id}")
def delete_live_analysis(id: int, db: Session = Depends(get_analysis_db)):
    record = db.query(LiveAnalysis).filter(LiveAnalysis.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录未找到")
    db.delete(record)
    db.commit()
    return {"message": "记录已删除"}


# 事件相关接口
# 查询所有事件
@app.get("/api/events", response_model=List[EventOut])
def get_all_events(db: Session = Depends(get_event_db)):
    """
    获取所有事件数据
    """
    events = db.query(Event).all()
    return events


# 获取事件相关公司的简称
@app.get("/api/events/shortnames")
def get_all_shortnames(db: Session = Depends(get_event_db)):
    """
    获取所有不重复的简称列表
    """
    shortnames = db.query(Event.简称).distinct().all()
    # db.query(...).distinct().all() 返回 [(简称1,), (简称2,), ...]
    return [item[0] for item in shortnames if item[0]]
# 根据序号查询事件
@app.get("/api/events/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_event_db)):
    """
    根据序号获取单个事件
    """
    event = db.query(Event).filter(Event.序号 == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="事件未找到")
    return event


# 创建新事件
@app.post("/api/events", response_model=EventOut)
def create_event(event_in: EventCreate, db: Session = Depends(get_event_db)):
    """
    新增事件
    """
    event = Event(**event_in.dict())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# 更新事件
@app.put("/api/events/{event_id}", response_model=EventOut)
def update_event(event_id: int, event_in: EventUpdate, db: Session = Depends(get_event_db)):
    """
    更新事件数据
    """
    event = db.query(Event).filter(Event.序号 == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="事件未找到")

    for key, value in event_in.dict(exclude_unset=True).items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return event


# 删除事件
@app.delete("/api/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_event_db)):
    """
    删除事件
    """
    event = db.query(Event).filter(Event.序号 == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="事件未找到")

    db.delete(event)
    db.commit()
    return {"detail": "事件已删除"}


# 板块相关接口
# 获取板块 整体数据
@app.get("/api/sector-trades")
def get_all_sector_trades(db: Session = Depends(get_sector_db)):
    """
    获取全行业交易数据
    - 返回: 行业数据列表（自动转为JSON）
    """
    sector_trades = db.query(SectorInfo).all()
    return sector_trades

# 按ID查询单个行业数据
@app.get("/api/sector-trades/{trade_id}")
def get_sector_trade_by_id(trade_id: int, db: Session = Depends(get_db)):
    """
    按ID查询行业数据
    - 参数: trade_id - 行业ID
    - 返回: 单个行业数据的JSON
    """
    trade = db.query(SectorInfo).filter(SectorInfo.id == trade_id).first()
    return trade if trade else {"error": "未找到该行业数据"}


# 按金额范围筛选
@app.get("/api/sector-trades/by-amount/")
def get_trades_by_amount_range(
        min_amount: Optional[int] = None,
        max_amount: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """
    按成交金额范围筛选
    - 参数:
        min_amount - 最小金额(可选)
        max_amount - 最大金额(可选)
    - 返回: 符合条件的数据列表
    """
    query = db.query(SectorInfo)
    if min_amount is not None:
        query = query.filter(SectorInfo.turnover_amount >= min_amount)
    if max_amount is not None:
        query = query.filter(SectorInfo.turnover_amount <= max_amount)
    return query.all()

# 新增数据
@app.post("/api/sector-trades/")
def create_sector_trade(trade_data: dict, db: Session = Depends(get_db)):
    """
    创建新的行业数据
    - 参数: trade_data - 包含各字段的字典
    - 返回: 创建成功的行业数据
    """
    new_trade = SectorInfo(**trade_data)
    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)
    return new_trade

# 更新数据
@app.put("/api/sector-trades/{trade_id}")
def update_sector_trade(
        trade_id: int,
        update_data: dict,
        db: Session = Depends(get_db)
):
    """
    更新行业数据
    - 参数:
        trade_id - 要更新的行业ID
        update_data - 包含更新字段的字典
    - 返回: 更新后的行业数据
    """
    db.query(SectorInfo).filter(SectorInfo.id == trade_id).update(update_data)
    db.commit()
    return db.query(SectorInfo).get(trade_id)

# 删除数据
@app.delete("/api/sector-trades/{trade_id}")
def delete_sector_trade(trade_id: int, db: Session = Depends(get_db)):
    """
    删除行业数据
    - 参数: trade_id - 要删除的行业ID
    - 返回: 操作结果
    """
    trade = db.query(SectorInfo).filter(SectorInfo.id == trade_id).first()
    if not trade:
        return {"error": "未找到该行业数据"}

    db.delete(trade)
    db.commit()
    return {"success": True, "deleted_id": trade_id}

# 舆情接口
# 获取所有舆情数据接口
@app.get("/api/sentiments")
def get_all_sentiments(db: Session = Depends(get_sentiment_db)):
    sentiments = db.query(PublicSentiment).all()  # 查询所有数据
    return sentiments

# 根据股票名称查询舆情数据接口
@app.get("/api/sentiment/{name}")
def get_sentiment(name: str, db: Session = Depends(get_sentiment_db)):
    sentiment = db.query(PublicSentiment).filter(PublicSentiment.name == name).first()
    if sentiment is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return sentiment




# 创建表（开发阶段使用）
Base.metadata.create_all(bind=engine)

# 依赖项，用于获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 宏观数据
@app.get("/api/macro-index")
def macro_index(db: Session = Depends(get_db)):
    results = (
        db.query(
            StockTotal.Date,
            func.avg(StockTotal.Close).label("avg_close"),
            func.sum(StockTotal.Volume).label("total_volume")
        )
        .filter(StockTotal.Close != None)
        .group_by(StockTotal.Date)
        .order_by(StockTotal.Date)
        .all()
    )

    return [
        {
            "date": row.Date,
            "avg_close": round(row.avg_close, 2) if row.avg_close else None,
            "total_volume": int(row.total_volume) if row.total_volume else 0
        }
        for row in results
    ]


# 模糊查询股票名称
@app.get("/api/search-stocks")
def search_stocks(
    keyword: str = Query(..., description="搜索关键词（股票名称或代码）"),
    db: Session = Depends(get_db)
):
    try:
        sql = text("""
            SELECT DISTINCT StockName, Code
            FROM stock_total
            WHERE StockName LIKE :kw OR CAST(Code AS CHAR) LIKE :kw
            LIMIT 20
        """)
        like_keyword = f"%{keyword}%"
        result = db.execute(sql, {"kw": like_keyword}).fetchall()

        # 格式化为 label/value 用于 el-select 组件
        stocks = [
            {"label": f"{row.StockName}（{row.Code}）", "value": row.StockName}
            for row in result if row.StockName and row.Code
        ]

        return stocks

    except Exception as e:
        print("🔴 查询失败：", str(e))
        return {"error": "数据库查询失败"}


# 查询股票数据
@app.get("/api/stock-data")
def get_stock_data(
    stock_name: str = Query(..., description="股票名称，例如 'BYD'"),
    db: Session = Depends(get_db)  # ⬅️ 使用依赖注入获取数据库连接
):
    print(f"查询股票:{stock_name}")
    try:
        sql = text("""
            SELECT Date, Open, Close, Low, High
            FROM stock_prices
            WHERE StockName = :stock_name
            ORDER BY Date ASC
        """)
        result = db.execute(sql, {"stock_name": stock_name}).fetchall()

        if not result:
            return {"error": f"未找到股票 {stock_name} 的数据"}

        x_data = [row.Date.strftime("%Y-%m-%d") for row in result]
        y_data = [[row.Open, row.Close, row.Low, row.High] for row in result]

        return {
            "xAxis": x_data,
            "yAxis": y_data,
            "title": f"{stock_name} Stock Prices"
        }

    except Exception as e:
        print("🔴 查询失败：", str(e))
        return {"error": "数据库查询失败"}






@app.get("/api/stock-summary")
def get_stock_summary(report_date: int = Query(None, alias="report_time"), db: Session = Depends(get_db)):
    query = db.query(StockSummary)

    # 如果提供了 report_date 参数，则按报告时间过滤
    if report_date:
        query = query.filter(StockSummary.报告时间 == report_date)

    # 排序并限制返回结果为 3 条记录
    summaries = (
        query.order_by(desc(StockSummary.报告时间))  # 按报告时间降序排列
        .limit(3)  # 限制只获取最新的 3 条记录
        .all()
    )

    return [
        {
            "id": s.id,
            "名称": s.名称,
            "流通股本": s.流通股本,
            "总市值": s.总市值,
            "平均市盈率": s.平均市盈率,
            "上市公司": s.上市公司,
            "上市股票": s.上市股票,
            "流通市值": s.流通市值,
            "报告时间": s.报告时间,
            "总股本": s.总股本,
        }
        for s in summaries
    ]

def test_get_stock_data(stock_name: str):
    # 获取数据库会话
    db: Session = next(get_db())

    # 调用你的函数并传入 stock_name 和 db
    result = get_stock_data(stock_name, db)

    # 打印返回的结果
    print(result)

def test_get_stock_name(key_word: str):
    # 获取数据库会话
    db: Session = next(get_db())

    # 调用你的函数并传入 stock_name 和 db
    result = search_stocks(key_word, db)

    # 打印返回的结果
    print(result)

def test_get_sum(report_date: int):
        # 获取数据库会话
        db: Session = next(get_db())

        # 调用你的函数并传入 stock_name 和 db
        result = get_stock_summary(report_date,db)

        # 打印返回的结果
        print(result)

def test_get_macro():
    # 获取数据库会话
    db: Session = next(get_db())

    # 调用你的函数并传入 stock_name 和 db
    result = macro_index( db)

    # 打印返回的结果
    print(result)

if __name__ == "__main__":
    # 测试函数，查询 "比亚迪" 的数据
    # test_get_stock_data("比亚迪")
    # test_get_stock_name("比亚")
    # test_get_sum(20250618)
    test_get_macro()