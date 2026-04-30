from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
from psycopg2 import pool
import os
from jose import jwt, JWTError
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET = "ddis-secret-key"
ALGORITHM = "HS256"

# Connection pool
connection_pool = None

@app.on_event("startup")
def startup():
    global connection_pool
    connection_pool = pool.ThreadedConnectionPool(
        minconn=2,
        maxconn=20,
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME", "fashion_shop"),
        user=os.getenv("DB_USER", "vikram"),
        password=os.getenv("DB_PASS", "vikram123")
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

# Route 1: Get item list with filters (Lab 2 - Task 1)
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

        cur.execute(f"SELECT COUNT(*) FROM items {where}", params)
        total = cur.fetchone()[0]

        cur.execute(f"""
            SELECT id, display_name, type, color, category,
                   price, discounted_price, data->>'description'
            FROM items {where}
            LIMIT %s OFFSET %s
        """, params + [page_size, offset])

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

# OpenSearch search route (Lab 2 - Task 2)
@app.get("/search")
def opensearch_search(q: str, size: int = 20):
    import urllib.request
    import json as jsonlib
    
    # Search in both title and description with fuzzy matching
    query = {
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["title^2", "description"],  # title boosted 2x
                "fuzziness": "AUTO"  # handles typos!
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
                "items": [
                    {
                        "id": h["_source"]["id"],
                        "title": h["_source"]["title"],
                        "description": h["_source"].get("description", ""),
                        "score": h["_score"]
                    } for h in hits
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))