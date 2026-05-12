import duckdb
import pandas as pd
import psycopg2
import time

# -----------------------------------
# CONNECT TO POSTGRESQL
# -----------------------------------

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="fashion_shop",
    user="vikram",
    password="vikram123",
)

# -----------------------------------
# LOAD DATA FROM POSTGRESQL
# -----------------------------------

items_df = pd.read_sql(
    """
SELECT
    id,
    type
FROM items
""",
    conn,
)

sales_df = pd.read_sql(
    """
SELECT
    item_id,
    sale_price,
    review_date,
    return_date
FROM sales
""",
    conn,
)

conn.close()

# -----------------------------------
# CREATE DUCKDB DATABASE
# -----------------------------------

db = duckdb.connect()

db.register("items", items_df)

db.register("sales", sales_df)

# -----------------------------------
# ANALYTICAL QUERY
# -----------------------------------

query = """
select
    type,
    count(*) as sales,
    sum(sale_price) as revenue,
    count(review_date) as reviews,
    count(return_date) as returns
from items i
join sales s on i.id = s.item_id
group by type
order by revenue desc
limit 10;
"""

# -----------------------------------
# MEASURE PERFORMANCE
# -----------------------------------

start = time.time()

result = db.execute(query).fetchdf()

elapsed = (time.time() - start) * 1000

print(result)

print(f"\nDuckDB Execution Time: {elapsed:.2f} ms")
