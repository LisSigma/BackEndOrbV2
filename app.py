# app.py
# FastAPI HWID + DLL size & method-count auth server
# Deploy to Render (e.g. https://backendorbv2.onrender.com)

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3
import os
import time
import jwt
from typing import Optional

# ---- CONFIG: set via env vars on Render (recommended) ----
ADMIN_KEY = os.getenv("ADMIN_KEY", "change_this_admin_key")
JWT_SECRET = os.getenv("JWT_SECRET", "change_this_jwt_secret")
JWT_ALGO = "HS256"
JWT_EXP_SECONDS = 60 * 60  # 1 hour

DB_PATH = "auth.db"

app = FastAPI(title="HWID + DLL Metrics Auth Service")


# ---- Pydantic models ----
class RegisterPayload(BaseModel):
    hwid: str
    file_size: int         # bytes
    method_count: int      # integer count of methods


class AuthPayload(BaseModel):
    hwid: str
    file_size: int
    method_count: int


class CheckPayload(BaseModel):
    token: str


# ---- DB utilities ----
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        hwid TEXT PRIMARY KEY,
        file_size INTEGER NOT NULL,
        method_count INTEGER NOT NULL,
        created_at INTEGER NOT NULL
    )
    """)
    conn.commit()
    conn.close()


def add_user(hwid: str, file_size: int, method_count: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (hwid, file_size, method_count, created_at) VALUES (?, ?, ?, ?)",
            (hwid, file_size, method_count, int(time.time()))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user(hwid: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT hwid, file_size, method_count, created_at FROM users WHERE hwid = ?", (hwid,))
    row = c.fetchone()
    conn.close()
    return row


init_db()


# ---- Endpoints ----
@app.get("/")
async def root():
    return {"ok": True, "service": "HWID + DLL Metrics Auth", "timestamp": int(time.time())}


# Admin-only register endpoint (requires X-ADMIN-KEY header)
@app.post("/register")
async def register(payload: RegisterPayload, x_admin_key: Optional[str] = Header(None)):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    created = add_user(payload.hwid, payload.file_size, payload.method_count)
    if created:
        return {"success": True, "message": "Registered"}
    else:
        return {"success": False, "message": "Already registered"}


# Auth endpoint: check hwid + file_size + method_count
@app.post("/auth")
async def auth(payload: AuthPayload):
    if not payload.hwid:
        raise HTTPException(status_code=400, detail="Missing hwid")
    row = get_user(payload.hwid)
    if not row:
        # Not registered
        raise HTTPException(status_code=401, detail="HWID not registered")
    registered_hwid, reg_file_size, reg_method_count, created_at = row

    # Compare both metrics
    if payload.file_size != reg_file_size or payload.method_count != reg_method_count:
        # Tamper detected
        raise HTTPException(status_code=403, detail="Metrics mismatch - tamper detected")

    # Issue JWT on success
    payload_jwt = {
        "hwid": payload.hwid,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXP_SECONDS
    }
    token = jwt.encode(payload_jwt, JWT_SECRET, algorithm=JWT_ALGO)
    return {"success": True, "token": token}


# Token verification (client can call to check still valid)
@app.post("/check")
async def check_token(payload: CheckPayload):
    token = payload.token
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return {"success": True, "hwid": data.get("hwid"), "exp": data.get("exp")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


# Admin list users (requires admin header)
@app.get("/list")
async def list_users(x_admin_key: Optional[str] = Header(None)):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT hwid, file_size, method_count, created_at FROM users")
    rows = c.fetchall()
    conn.close()
    users = [{"hwid": r[0], "file_size": r[1], "method_count": r[2], "created_at": r[3]} for r in rows]
    return {"count": len(users), "users": users}
