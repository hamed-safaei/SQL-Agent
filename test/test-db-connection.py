from app.core.database.clientdb import run_query

rows, cols = run_query("SELECT TOP 5 name FROM sys.tables")

print(cols)
print(rows)
