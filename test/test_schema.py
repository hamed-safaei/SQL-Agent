# from app.database import get_db_schema_text

# schema_text = get_db_schema_text()
# print(schema_text)





from app.clientdb import run_sql_query

test = run_sql_query("SELECT * FROM sales.staffs")
print(test)