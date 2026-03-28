from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
import psycopg2, os
from jose import jwt, JWTError
from datetime import datetime, timedelta

app = FastAPI()

SECRET = "ddis-secret-key"
ALGORITHM = "HS256"

# ── Database connection ──────────────────────────────────────────
def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME", "fashion_shop"),
        user=os.getenv("DB_USER", "vikram"),
        password=os.getenv("DB_PASS", "vikram123")
    )

# ── JWT helpers ──────────────────────────────────────────────────
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

# ── Route 1: Get item list (paginated) ───────────────────────────
@app.get("/items")
def get_items(page: int = 1, page_size: int = 20):
    db = get_db()
    cur = db.cursor()
    offset = (page - 1) * page_size
    cur.execute("""
        SELECT id,
               data->>'productDisplayName' as display_name,
               data->'articleType'->>'typeName' as type,
               data->>'baseColour' as color,
               (data->>'price')::float as price,
               (data->>'discountedPrice')::float as discounted_price
        FROM items
        LIMIT %s OFFSET %s
    """, (page_size, offset))
    rows = cur.fetchall()
    db.close()
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

# ── Route 2: Get item details ────────────────────────────────────
@app.get("/item/{item_id}")
def get_item(item_id: int):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT id, data, avg_rating, num_reviews, return_quota
        FROM items WHERE id = %s
    """, (item_id,))
    row = cur.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return {
        "id": row[0],
        "data": row[1],
        "avg_rating": row[2],
        "num_reviews": row[3],
        "return_quota": row[4]
    }

# ── Route 3: Login ───────────────────────────────────────────────
@app.post("/login")
def login(body: dict):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT uid FROM users
        WHERE email = %s
        AND password = crypt(%s, password)
    """, (body.get("email"), body.get("password")))
    row = cur.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": make_token(row[0])}

# ── Route 4: Get user details ────────────────────────────────────
@app.get("/user/{user_id}")
def get_user(user_id: str, token_uid: str = Depends(verify_token)):
    if user_id != token_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT uid, email, first_name, last_name, country
        FROM users WHERE uid = %s
    """, (user_id,))
    row = cur.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "uid": row[0],
        "email": row[1],
        "first_name": row[2],
        "last_name": row[3],
        "country": row[4]
    }

# ── Route 5: Get user sales ──────────────────────────────────────
@app.get("/user/{user_id}/sales")
def get_user_sales(user_id: str, token_uid: str = Depends(verify_token)):
    if user_id != token_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT id, item_id, sale_date, sale_price, quantity, rating
        FROM sales WHERE uid = %s
    """, (user_id,))
    rows = cur.fetchall()
    db.close()
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

# ── Route 6: Post a sale (transactional) ────────────────────────
@app.post("/sales/")
def post_sale(body: dict, token_uid: str = Depends(verify_token)):
    if body.get("user_id") != token_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("BEGIN")
        cur.execute("""
            SELECT in_stock,
                   (data->>'price')::float,
                   (data->>'discountedPrice')::float
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
            body.get("quantity", 1), item[1], None  # discount = None for now
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
        db.close()

# ── Route 7: Update a sale ───────────────────────────────────────
@app.patch("/sales/{sale_id}")
def update_sale(sale_id: int, body: dict, token_uid: str = Depends(verify_token)):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT uid, item_id FROM sales WHERE id = %s", (sale_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sale not found")
    if row[0] != token_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    item_id = row[1]
    try:
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
                        SELECT AVG(rating) FROM sales
                        WHERE item_id = %s AND rating IS NOT NULL
                    ),
                    num_reviews = (
                        SELECT COUNT(*) FROM sales
                        WHERE item_id = %s AND rating IS NOT NULL
                    )
                WHERE id = %s
            """, (item_id, item_id, item_id))
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
        db.close()