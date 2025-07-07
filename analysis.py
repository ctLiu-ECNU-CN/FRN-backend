import pymysql
import pandas as pd
from datetime import datetime, timedelta

# 连接 stock_live 数据库
stock_conn = pymysql.connect(
    host='192.168.5.2',
    user='root',
    password='34793479',
    database='stock_live',
    charset='utf8mb4'
)
cursor = stock_conn.cursor()
cursor.execute("SHOW TABLES")
tables = [row[0] for row in cursor.fetchall() if row[0].startswith("A股分钟行情_")]

now = datetime.now()
anomaly_records = []

for table in tables:
    try:
        # 读取数据
        df = pd.read_sql(f"SELECT * FROM `{table}`", stock_conn)

        # 检查表是否为空或缺必要列
        required_cols = {'day', 'volume', 'close', 'high', 'low'}
        if df.empty or not required_cols.issubset(df.columns):
            print(f"⚠️ 表 {table} 数据为空或缺少关键字段，已跳过。")
            continue

        # 转换时间字段
        df['day'] = pd.to_datetime(df['day'], errors='coerce')
        df.dropna(subset=['day'], inplace=True)

        # 筛选最近 30000 分钟数据
        df_recent = df[df['day'] >= now - timedelta(minutes=30000)]
        if len(df_recent) < 2:
            print(f"⚠️ 表 {table} 最近数据不足，跳过。")
            continue

        stock_name = table.replace("A股分钟行情_", "")
        last_row = df_recent.iloc[-1]
        today_rows = df_recent[df_recent['day'].dt.date == now.date()]

        # 成交量激增检测
        avg_volume = df_recent['volume'].iloc[:-1].mean()
        if avg_volume > 0 and last_row['volume'] > avg_volume * 3:
            anomaly_records.append({
                "stock": stock_name,
                "timestamp": last_row['day'],
                "event_type": "volume_spike",
                "event": f"成交量激增（现量: {last_row['volume']}, 均量: {int(avg_volume)}）"
            })

        # 收盘价波动检测
        close_mean = df_recent['close'].iloc[:-1].mean()
        if close_mean > 0 and abs(last_row['close'] - close_mean) / close_mean > 0.02:
            anomaly_records.append({
                "stock": stock_name,
                "timestamp": last_row['day'],
                "event_type": "close_fluctuation",
                "event": f"收盘价波动超2%（现: {last_row['close']:.2f}, 均: {close_mean:.2f}）"
            })

        # 盘中新高
        if not today_rows.empty and last_row['high'] >= today_rows['high'].max():
            anomaly_records.append({
                "stock": stock_name,
                "timestamp": last_row['day'],
                "event_type": "intraday_high",
                "event": "盘中新高"
            })

        # 盘中新低
        if not today_rows.empty and last_row['low'] <= today_rows['low'].min():
            anomaly_records.append({
                "stock": stock_name,
                "timestamp": last_row['day'],
                "event_type": "intraday_low",
                "event": "盘中新低"
            })

    except Exception as e:
        print(f"❌ 表 {table} 分析异常：{e}")
        continue

cursor.close()
stock_conn.close()

# 写入 report.live_analysis 表
if anomaly_records:
    try:
        report_conn = pymysql.connect(
            host='192.168.5.2',
            user='root',
            password='34793479',
            database='report',
            charset='utf8mb4'
        )
        with report_conn.cursor() as cursor:
            for anomaly in anomaly_records:
                sql = """
                    INSERT INTO live_analysis (stock, event_type, timestamp, event)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    anomaly["stock"],
                    anomaly["event_type"],
                    anomaly["timestamp"],
                    anomaly["event"]
                ))
            report_conn.commit()
        report_conn.close()
        print(f"✅ 分析完成，已写入 {len(anomaly_records)} 条异常记录")
    except Exception as e:
        print(f"❌ 异常记录写入失败：{e}")
else:
    print("✅ 无显著异常")
