# Data Loading Process — Lab 1

## Dataset Source
https://db.iue.haw-kiel.de/ddis/fashion-shop/

## Files Downloaded
- create_tables.sql
- users.csv (69MB)
- sales.csv (1.2GB)
- items.zip (82MB — 44,446 JSON files)

## Loading Steps

### 1. Create tables
```sql
\i /tmp/create_tables.sql
```

### 2. Load users
```sql
\COPY users FROM '/tmp/users.csv' CSV HEADER;
-- Result: 540,357 rows
```

### 3. Load items (JSON files)
```sql
DO $$
DECLARE
  item_file TEXT;
  item_json JSON;
  item_id INT;
BEGIN
  FOR item_file IN SELECT pg_ls_dir('/tmp/items') LOOP
    item_json := pg_read_file('/tmp/items/' || item_file)::JSON;
    item_id := (item_json->>'id')::INT;
    INSERT INTO items (id, data) VALUES (item_id, item_json)
    ON CONFLICT DO NOTHING;
  END LOOP;
END $$;
-- Result: 44,446 rows
```

### 4. Load sales
```sql
\COPY sales (id, item_id, uid, sale_date, sale_price, discount, quantity, 
review_date, review_text, review_text_lang, rating, return_date, return_reason) 
FROM '/tmp/sales.csv' WITH (FORMAT csv, HEADER true, ESCAPE '\');
-- Result: 10,343,240 rows
```

### 5. Fix sequence after import
```sql
SELECT setval('sales_id_seq', (SELECT MAX(id) FROM sales));
```

### 6. Verify row counts
```sql
SELECT 'users' as table_name, COUNT(*) FROM users
UNION ALL SELECT 'items', COUNT(*) FROM items
UNION ALL SELECT 'sales', COUNT(*) FROM sales;
```

## Row Counts
| Table | Rows |
|---|---|
| users | 540,357 |
| items | 44,446 |
| sales | 10,343,240 |
