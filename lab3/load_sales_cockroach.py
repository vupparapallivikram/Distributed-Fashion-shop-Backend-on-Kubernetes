import psycopg2
import csv

conn = psycopg2.connect(
    host="localhost",
    port=26257,
    database="fashion_shop",
    user="vikram",
    sslmode="disable"
)
cur = conn.cursor()

print("Loading sales...")
count = 0
errors = 0

with open('/Users/kalamakuntlarakeshreddy/ddis-data/sales.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    batch = []
    
    for row in reader:
        try:
            batch.append((
                int(row['id']),
                int(row['item_id']),
                row['uid'],
                row['sale_date'] or None,
                float(row['sale_price']),
                float(row['discount']) if row['discount'] else None,
                int(row['quantity']),
                row['review_date'] or None,
                row['review_text'] or None,
                row['review_text_lang'] or None,
                int(row['rating']) if row['rating'] else None,
                row['return_date'] or None,
                row['return_reason'] or None
            ))
            
            if len(batch) >= 1000:
                cur.executemany("""
                    INSERT INTO sales (id, item_id, uid, sale_date, sale_price, 
                    discount, quantity, review_date, review_text, review_text_lang,
                    rating, return_date, return_reason)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT DO NOTHING
                """, batch)
                conn.commit()
                count += len(batch)
                batch = []
                print(f"Loaded: {count}")
        except Exception as e:
            errors += 1
            continue
    
    if batch:
        cur.executemany("""
            INSERT INTO sales (id, item_id, uid, sale_date, sale_price,
            discount, quantity, review_date, review_text, review_text_lang,
            rating, return_date, return_reason)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT DO NOTHING
        """, batch)
        conn.commit()
        count += len(batch)

print(f"Done! Loaded {count} sales, {errors} errors")
cur.close()
conn.close()
