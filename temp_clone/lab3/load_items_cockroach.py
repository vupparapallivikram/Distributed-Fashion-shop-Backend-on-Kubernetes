import psycopg2
import json
import os

# CockroachDB is PostgreSQL compatible!
conn = psycopg2.connect(
    host="localhost",
    port=26257,
    database="fashion_shop",
    user="vikram",
    sslmode="disable"
)
cur = conn.cursor()

# Add columns needed
cur.execute("""
ALTER TABLE items ADD COLUMN IF NOT EXISTS display_name TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS price FLOAT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS discounted_price FLOAT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS color TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS type TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS category TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS in_stock INT DEFAULT 2;
ALTER TABLE items ADD COLUMN IF NOT EXISTS avg_rating FLOAT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS num_reviews INT DEFAULT 0;
ALTER TABLE items ADD COLUMN IF NOT EXISTS return_quota FLOAT;
""")
conn.commit()

# Load JSON files
items_dir = os.path.expanduser("~/ddis-data/item_data")
files = os.listdir(items_dir)
total = len(files)
success = 0

for i, filename in enumerate(files):
    if not filename.endswith('.json'):
        continue
    with open(os.path.join(items_dir, filename)) as f:
        data = json.load(f)
    
    item_id = int(data.get('id', 0))
    
    cur.execute("""
        INSERT INTO items (id, data, display_name, price, discounted_price, color, type, in_stock)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 2)
        ON CONFLICT DO NOTHING
    """, (
        item_id,
        json.dumps(data),
        data.get('productDisplayName'),
        float(data.get('price', 0) or 0),
        float(data.get('discountedPrice', 0) or 0),
        data.get('baseColour'),
        data.get('articleType', {}).get('typeName') if isinstance(data.get('articleType'), dict) else None
    ))
    success += 1
    
    if (i+1) % 1000 == 0:
        conn.commit()
        print(f"Progress: {i+1}/{total}")

conn.commit()
print(f"Done! Loaded {success} items")
cur.close()
conn.close()
