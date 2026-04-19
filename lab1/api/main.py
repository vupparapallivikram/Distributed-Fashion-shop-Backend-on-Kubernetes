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

# Route 1: Get item list (paginated) - NO JSON parsing
@app.get("/items")
def get_items(
    page: int = 1,
    page_size: int = 20,
    color: str = None,
    type: str = None,
    category: str = None,
    price_min: float = None,
    price_max: float = None
):
    db = get_db()
    try:
        cur = db.cursor()
        offset = (page - 1) * page_size
        query = """
            SELECT id, display_name, type, color, price, discounted_price
            FROM items
            WHERE 1=1
        """
        params = []

        if color is not None:
            query += " AND color = %s"
            params.append(color)
        if type is not None:
            query += " AND type = %s"
            params.append(type)
        if category is not None:
            query += " AND category = %s"
            params.append(category)
        if price_min is not None:
            query += " AND price >= %s"
            params.append(price_min)
        if price_max is not None:
            query += " AND price <= %s"
            params.append(price_max)

        query += " LIMIT %s OFFSET %s"
        params.extend([page_size, offset])

        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "display_name": r[1],
                "type": r[2],
                "color": r[3],
                "price": r[4],
                "discounted_price": r[5]
            } for r in rows
        ]
    finally:
        connection_pool.putconn(db)

# Route 2: Get item details - NO JSON parsing
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
        return {
            "id": row[0],
            "display_name": row[1],
            "type": row[2],
            "color": row[3],
            "price": row[4],
            "discounted_price": row[5],
            "avg_rating": row[6],
            "num_reviews": row[7],
            "return_quota": row[8]
        }
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
            WHERE email = %s
            AND password = crypt(%s, password)
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
        return {
            "uid": row[0],
            "email": row[1],
            "first_name": row[2],
            "last_name": row[3],
            "country": row[4]
        }
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
        return [
            {
                "id": r[0],
                "item_id": r[1],
                "sale_date": str(r[2]),
                "sale_price": float(r[3]),
                "quantity": r[4],
                "rating": r[5]
            } for r in rows
        ]
    finally:
        connection_pool.putconn(db)

# Route 6: Post a sale (transactional)
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
        """, (
            body["item_id"], token_uid,
            body.get("quantity", 1), item[1], None
        ))
        sale_id = cur.fetchone()[0]
        cur.execute("""
            UPDATE items SET in_stock = in_stock - %s WHERE id = %s
        """, (body.get("quantity", 1), body["item_id"]))
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
                    avg_rating = (
                        (COALESCE(avg_rating, 0) * COALESCE(num_reviews, 0) + %s)
                        / (COALESCE(num_reviews, 0) + 1)
                    ),
                    num_reviews = COALESCE(num_reviews, 0) + 1
                WHERE id = %s
            """, (body.get("rating", 0), item_id))
        if "return_reason" in body:
            cur.execute("""
                UPDATE sales SET
                    return_reason = %s,
                    return_date = NOW()
                WHERE id = %s
            """, (body["return_reason"], sale_id))
            cur.execute("""
                UPDATE items SET
                    return_quota = (
                        SELECT COUNT(return_date)::float / NULLIF(COUNT(*), 0)
                        FROM sales WHERE item_id = %s
                    )
                WHERE id = %s
            """, (item_id, item_id))
        db.commit()
        return {"status": "updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        connection_pool.putconn(db)