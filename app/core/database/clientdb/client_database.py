from sqlalchemy import create_engine, text
import psycopg2
from app.core import settings
from typing import Dict, List, Any

SCHEMA_QUERY = """
SELECT 
    table_schema,
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
ORDER BY table_schema, table_name, ordinal_position;
"""

def get_connection_string():
    return 'postgresql://hamed:1234@localhost:5432/bikestore'

_ENGINE = None

def get_engine():
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = create_engine(get_connection_string())
    return _ENGINE

def fetch_raw_schema_rows():
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text(SCHEMA_QUERY)).fetchall()
    return rows

def build_schema_dict(rows) -> Dict[str, List[str]]:
    schema_dict: Dict[str, List[str]] = {}
    for schema, table, column, dtype in rows:
        full_table_name = f"{schema}.{table}"
        if full_table_name not in schema_dict:
            schema_dict[full_table_name] = []
        schema_dict[full_table_name].append(f"{column} ({dtype})")
    return schema_dict

def format_schema_for_llm(schema_dict: Dict[str, List[str]]) -> str:
    lines: List[str] = ["Database Schema:"]
    for table, columns in schema_dict.items():
        lines.append(f"- Table: {table}")
        lines.append("  Columns: " + ", ".join(columns))
        lines.append("")
    return "\n".join(lines)

def get_db_schema_text() -> str:
    rows = fetch_raw_schema_rows()
    schema_dict = build_schema_dict(rows)
    return format_schema_for_llm(schema_dict)

def run_sql_query(sql: str):
    conn = psycopg2.connect(
        host="localhost",
        database="bikestore",
        user="hamed",
        password="1234",
        port="5432"
    )
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        # بررسی اینکه آیا کوئری خروجی دارد یا خیر
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
        else:
            result = []
        return result
    finally:
        cursor.close()
        conn.close()
