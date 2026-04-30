import psycopg2
import requests
import json

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="fashion_shop",
    user="vikram",
    password="vikram123"
)
cur = conn.cursor()

# Get all items with reviews
print("Fetching items from PostgreSQL...")
cur.execute("""
    SELECT 
        i.id,
        i.display_name as title,
        i.data->>'description' as description,
        ARRAY_AGG(s.review_text) FILTER (WHERE s.review_text IS NOT NULL) as reviews
    FROM items i
    LEFT JOIN sales s ON i.id = s.item_id
    GROUP BY i.id, i.display_name, i.data->>'description'
    LIMIT 44446
""")

rows = cur.fetchall()
print(f"Found {len(rows)} items")

# Sync to OpenSearch
OPENSEARCH = "http://localhost:9200"
success = 0
errors = 0

for i, row in enumerate(rows):
    item_id, title, description, reviews = row
    
    doc = {
        "id": item_id,
        "title": title or "",
        "description": description or "",
        "reviews": reviews or []
    }
    
    r = requests.put(
        f"{OPENSEARCH}/items/_doc/{item_id}",
        headers={"Content-Type": "application/json"},
        json=doc
    )
    
    if r.status_code in [200, 201]:
        success += 1
    else:
        errors += 1
    
    if (i+1) % 1000 == 0:
        print(f"Progress: {i+1}/{len(rows)} — success: {success}, errors: {errors}")

print(f"\nDone! Success: {success}, Errors: {errors}")
cur.close()
conn.close()
