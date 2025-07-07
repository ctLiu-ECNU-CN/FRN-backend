from fastapi import HTTPException
from sqlalchemy import MetaData, Table

metadata = MetaData()

def get_sector_table(table_name: str, engine):
    metadata.reflect(bind=engine)
    if table_name not in metadata.tables:
        raise HTTPException(status_code=404, detail=f"表 {table_name} 不存在")
    return Table(table_name, metadata, autoload_with=engine)