from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
from psycopg2 import pool
import os
from jose import jwt, JWTError
from datetime import datetime, timedelta
import requests
import urllib3

urllib3.disable_warnings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET = "ddis-secret-key"
ALGORITHM = "HS256"

connection_pool = None

@app.on_event("startup")
def startup():
    global connection_pool
    connection_pool = pool.ThreadedConnectionPool(
        minconn=2,
        maxconn=20,
        host=os.getenv("DB_HOST", "postgres"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "fashion_shop"),
        user=os.getenv("DB_USER", "vikram"),
        password=os.getenv("DB_PASS", "vikram123"),
        sslmode=os.getenv("DB_SSLMODE", "require")
    )

def get_db():
    return connection_pool.getconn()

def make_token(uid: str):
    payload = {
        "sub": uid,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = jwt.decode(
            authorization.split(" ")[1],
            SECRET,
            algorithms=[ALGORITHM]
        )
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Route 1: Get item list with filters
@app.get("/items")
def get_items(
    page: int = 1,
    page_size: int = 20,
    color: str = None,
    type: str = None,
    category: str = None,
    price_min: float = None,
    price_max: float = None,
    search: str = None
):
    db = get_db()
    try:
        cur = db.cursor()
        offset = (page - 1) * page_size
        params = []
        where = "WHERE 1=1"

        if color:
            where += " AND color = ANY(%s)"
            params.append([c.strip() for c in color.split(",")])
        if type:
            where += " AND type = ANY(%s)"
            params.append([t.strip() for t in type.split(",")])
        if category:
            where += " AND category = ANY(%s)"
            params.append([c.strip() for c in category.split(",")])
        if price_min is not None:
            where += " AND discounted_price >= %s"
            params.append(price_min)
        if price_max is not None:
            where += " AND discounted_price <= %s"
            params.append(price_max)
        if search:
            where += " AND to_tsvector('english', COALESCE(display_name,'') || ' ' || COALESCE(data->>'description','')) @@ websearch_to_tsquery('english', %s)"
            params.append(search)

        cur.execute(f"SELECT COUNT(*) FROM items {where}", tuple(params))
        total = cur.fetchone()[0]

        cur.execute(f"""
            SELECT id, display_name, type, color, category,
                   price, discounted_price, data->>'description'
            FROM items {where}
            LIMIT %s OFFSET %s
        """, tuple(params) + (page_size, offset))

        rows = cur.fetchall()
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [{"id": r[0], "display_name": r[1], "type": r[2],
                       "color": r[3], "category": r[4], "price": r[5],
                       "discounted_price": r[6], "description": r[7]}
                      for r in rows]
        }
    finally:
        connection_pool.putconn(db)

# Route 2: Get item details
@app.get("/item/{item_id}")
def get_item(item_id: int):
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT id, display_name, type, color, price, discounted_price,
                   avg_rating, num_reviews, return_quota
            FROM items WHERE id = %s
        """, (item_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"id": row[0], "display_name": row[1], "type": row[2],
                "color": row[3], "price": row[4], "discounted_price": row[5],
                "avg_rating": row[6], "num_reviews": row[7], "return_quota": row[8]}
    finally:
        connection_pool.putconn(db)

# Route 3: Login
@app.post("/login")
def login(body: dict):
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT uid FROM users
            WHERE email = %s AND password = crypt(%s, password)
        """, (body.get("email"), body.get("password")))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"token": make_token(row[0])}
    finally:
        connection_pool.putconn(db)

# Route 4: Get user details
@app.get("/user/{user_id}")
def get_user(user_id: str, token_uid: str = Depends(verify_token)):
    if user_id != token_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT uid, email, first_name, last_name, country
            FROM users WHERE uid = %s
        """, (user_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return {"uid": row[0], "email": row[1], "first_name": row[2],
                "last_name": row[3], "country": row[4]}
    finally:
        connection_pool.putconn(db)

# Route 5: Get user sales
@app.get("/user/{user_id}/sales")
def get_user_sales(user_id: str, token_uid: str = Depends(verify_token)):
    if user_id != token_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT id, item_id, sale_date, sale_price, quantity, rating
            FROM sales WHERE uid = %s
        """, (user_id,))
        rows = cur.fetchall()
        return [{"id": r[0], "item_id": r[1], "sale_date": str(r[2]),
                 "sale_price": float(r[3]), "quantity": r[4], "rating": r[5]}
                for r in rows]
    finally:
        connection_pool.putconn(db)

# Route 6: Post a sale
@app.post("/sales/")
def post_sale(body: dict, token_uid: str = Depends(verify_token)):
    if body.get("user_id") != token_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute("BEGIN")
        cur.execute("""
            SELECT in_stock, price, discounted_price
            FROM items WHERE id = %s FOR UPDATE
        """, (body["item_id"],))
        item = cur.fetchone()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if item[0] < body.get("quantity", 1):
            raise HTTPException(status_code=400, detail="Out of stock")
        cur.execute("""
            INSERT INTO sales (item_id, uid, quantity, sale_price, discount)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (body["item_id"], token_uid, body.get("quantity", 1), item[1], None))
        sale_id = cur.fetchone()[0]
        cur.execute("UPDATE items SET in_stock = in_stock - %s WHERE id = %s",
                    (body.get("quantity", 1), body["item_id"]))
        db.commit()
        return {"sale_id": sale_id}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        connection_pool.putconn(db)

# Route 7: Update a sale
@app.patch("/sales/{sale_id}")
def update_sale(sale_id: int, body: dict, token_uid: str = Depends(verify_token)):
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute("SELECT uid, item_id FROM sales WHERE id = %s", (sale_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Sale not found")
        if row[0] != token_uid:
            raise HTTPException(status_code=403, detail="Forbidden")
        item_id = row[1]
        cur.execute("BEGIN")
        if "rating" in body or "review" in body:
            cur.execute("""
                UPDATE sales SET
                    rating = COALESCE(%s, rating),
                    review_text = COALESCE(%s, review_text),
                    review_date = NOW()
                WHERE id = %s
            """, (body.get("rating"), body.get("review"), sale_id))
            cur.execute("""
                UPDATE items SET
                    avg_rating = ((COALESCE(avg_rating,0) * COALESCE(num_reviews,0) + %s)
                    / (COALESCE(num_reviews,0) + 1)),
                    num_reviews = COALESCE(num_reviews,0) + 1
                WHERE id = %s
            """, (body.get("rating", 0), item_id))
        if "return_reason" in body:
            cur.execute("""
                UPDATE sales SET return_reason = %s, return_date = NOW()
                WHERE id = %s
            """, (body["return_reason"], sale_id))
        db.commit()
        return {"status": "updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        connection_pool.putconn(db)

# OpenSearch search
@app.get("/search")
def opensearch_search(q: str, size: int = 20):
    import urllib.request
    import json as jsonlib
    query = {
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["title^2", "description"],
                "fuzziness": "AUTO"
            }
        },
        "size": size
    }
    data = jsonlib.dumps(query).encode()
    req = urllib.request.Request(
        "http://opensearch:9200/items/_search",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            result = jsonlib.loads(response.read())
            hits = result["hits"]["hits"]
            return {
                "total": result["hits"]["total"]["value"],
                "items": [{"id": h["_source"]["id"], "title": h["_source"]["title"],
                           "description": h["_source"].get("description", ""),
                           "score": h["_score"]} for h in hits]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vector Search
@app.get("/vector-search")
def vector_search(q: str, size: int = 20):
    embedding_response = requests.post(
        "https://db.iue.haw-kiel.de/ollama/api/embeddings",
        headers={"Content-Type": "application/json", "X-Api-Key": "42"},
        json={"model": "nomic-embed-text-v2-moe:latest", "prompt": q},
        verify=False,
        timeout=60
    )
    embedding = embedding_response.json()["embedding"]
    query = {
        "size": size,
        "query": {
            "knn": {
                "embedding": {
                    "vector": embedding,
                    "k": size
                }
            }
        }
    }
    try:
        response = requests.get(
            "http://opensearch:9200/items_vector/_search",
            headers={"Content-Type": "application/json"},
            json=query,
            timeout=60
        )
        result = response.json()
        hits = result["hits"]["hits"]
        return {
            "total": len(hits),
            "items": [{"id": h["_source"]["id"], "display_name": h["_source"]["title"],
                       "description": h["_source"].get("description", ""),
                       "score": h["_score"]} for h in hits]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))