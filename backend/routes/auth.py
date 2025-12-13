"""
Authentication routes for Smart Financial Advisor
Simple session-based auth with search history
"""
from fastapi import APIRouter, HTTPException, Response, Cookie
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import hashlib
import secrets
import json

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Simple in-memory storage (in production, use a database)
users_db = {}
sessions = {}
search_history = {}  # user_id -> list of searches


class UserRegister(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class SearchItem(BaseModel):
    symbol: str
    timestamp: str = None
    type: str = "stock"  # stock, sentiment, portfolio


def hash_password(password: str) -> str:
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_session(user_id: str) -> str:
    """Create a new session token"""
    token = secrets.token_urlsafe(32)
    sessions[token] = {
        "user_id": user_id,
        "created": datetime.now().isoformat()
    }
    return token


def get_user_from_session(session_token: str) -> Optional[dict]:
    """Get user from session token"""
    if session_token and session_token in sessions:
        user_id = sessions[session_token]["user_id"]
        if user_id in users_db:
            return users_db[user_id]
    return None


@router.post("/register")
async def register(user: UserRegister, response: Response):
    """Register a new user"""
    email = user.email.lower()
    
    if email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    users_db[email] = {
        "id": email,
        "name": user.name,
        "email": email,
        "password_hash": hash_password(user.password),
        "created": datetime.now().isoformat()
    }
    
    # Initialize search history for user
    search_history[email] = []
    
    return {"message": "Account created successfully", "email": email}


@router.post("/login")
async def login(user: UserLogin, response: Response):
    """Login and create session"""
    email = user.email.lower()
    
    if email not in users_db:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    stored_user = users_db[email]
    if stored_user["password_hash"] != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create session
    session_token = create_session(email)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=86400 * 7,  # 7 days
        samesite="lax"
    )
    
    return {
        "message": "Login successful",
        "user": {
            "name": stored_user["name"],
            "email": stored_user["email"]
        }
    }


@router.post("/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    """Logout and clear session"""
    if session_token and session_token in sessions:
        del sessions[session_token]
    
    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user(session_token: Optional[str] = Cookie(None)):
    """Get current logged in user"""
    user = get_user_from_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "name": user["name"],
        "email": user["email"]
    }


@router.get("/check")
async def check_auth(session_token: Optional[str] = Cookie(None)):
    """Check if user is authenticated"""
    user = get_user_from_session(session_token)
    return {"authenticated": user is not None}


# Search History Endpoints
@router.post("/history/add")
async def add_search_history(item: SearchItem, session_token: Optional[str] = Cookie(None)):
    """Add item to search history"""
    user = get_user_from_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user["email"]
    if user_id not in search_history:
        search_history[user_id] = []
    
    # Add to history (avoid duplicates, keep recent)
    history = search_history[user_id]
    
    # Remove if already exists
    history = [h for h in history if h["symbol"] != item.symbol]
    
    # Add new entry
    history.insert(0, {
        "symbol": item.symbol.upper(),
        "timestamp": datetime.now().isoformat(),
        "type": item.type
    })
    
    # Keep only last 20
    search_history[user_id] = history[:20]
    
    return {"message": "Added to history", "history_count": len(search_history[user_id])}


@router.get("/history")
async def get_search_history(session_token: Optional[str] = Cookie(None)):
    """Get user's search history"""
    user = get_user_from_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user["email"]
    history = search_history.get(user_id, [])
    
    return {"history": history}


@router.delete("/history/clear")
async def clear_search_history(session_token: Optional[str] = Cookie(None)):
    """Clear user's search history"""
    user = get_user_from_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user["email"]
    search_history[user_id] = []
    
    return {"message": "History cleared"}


# Demo user for testing (remove in production)
def init_demo_user():
    """Initialize a demo user for testing"""
    demo_email = "demo@example.com"
    if demo_email not in users_db:
        users_db[demo_email] = {
            "id": demo_email,
            "name": "Demo User",
            "email": demo_email,
            "password_hash": hash_password("demo123"),
            "created": datetime.now().isoformat()
        }
        search_history[demo_email] = [
            {"symbol": "AAPL", "timestamp": datetime.now().isoformat(), "type": "stock"},
            {"symbol": "GOOGL", "timestamp": datetime.now().isoformat(), "type": "stock"},
            {"symbol": "TSLA", "timestamp": datetime.now().isoformat(), "type": "sentiment"},
        ]

# Initialize demo user on module load
init_demo_user()
