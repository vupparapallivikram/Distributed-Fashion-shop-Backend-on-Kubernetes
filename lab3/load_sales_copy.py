import psycopg2
import csv
import io

conn = psycopg2.connect(
    host="localhost",
    port=26257,
    database="fashion_shop",
    user="vikram",
    sslmode="disable"
)
cur = conn.cursor()

print("Loading sales via COPY...")
count = 0
batch_size = 50000
batch = []

fields = ['id','item_id','uid','sale_date','sale_price','discount','quantity',
          'review_date','review_text','review_text_lang','rating','return_date','return_reason']

with open('/Users/kalamakuntlarakeshreddy/ddis-data/sales.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        try:
            line = '\t'.join([
                row.get('id',''),
                row.get('item_id',''),
                row.get('uid',''),
                row.get('sale_date','') or '\\N',
                row.get('sale_price','') or '\\N',
                row.get('discount','') or '\\N',
                row.get('quantity','') or '\\N',
                row.get('review_date','') or '\\N',
                (row.get('review_text','') or '').replace('\t',' ').replace('\n',' ').replace('\r',' ') or '\\N',
                row.get('review_text_lang','') or '\\N',
                row.get('rating','') or '\\N',
                row.get('return_date','') or '\\N',
                row.get('return_reason','') or '\\N'
            ])
            batch.append(line)
            
            if len(batch) >= batch_size:
                data = '\n'.join(batch) + '\n'
                cur.copy_from(
                    io.StringIO(data),
                    'sales',
                    columns=fields,
                    null='\\N',
                    sep='\t'
                )
                conn.commit()
                count += len(batch)
                batch = []
                print(f"Loaded: {count}")
                
        except Exception as e:
            batch = []
            continue

if batch:
    try:
        data = '\n'.join(batch) + '\n'
        cur.copy_from(
            io.StringIO(data),
            'sales',
            columns=fields,
            null='\\N',
            sep='\t'
        )
        conn.commit()
        count += len(batch)
    except Exception as e:
        print(f"Final batch error: {e}")

print(f"Done! Loaded {count} sales")
cur.close()
conn.close()
