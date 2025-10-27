from fastapi import APIRouter, HTTPException, status, Depends
from ..models import UserCreate, UserLogin, Token, User
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user
from ..database import get_mongodb
from datetime import datetime
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    db = get_mongodb()
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)
    
    new_user = {
        "user_id": user_id,
        "email": user.email,
        "username": user.username,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
    }
    
    await db.users.insert_one(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user_id, "email": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    db = get_mongodb()
    
    # Find user
    db_user = await db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": db_user["user_id"], "email": db_user["email"]}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    db = get_mongodb()
    
    user = await db.users.find_one({"user_id": current_user["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user["user_id"],
        "email": user["email"],
        "username": user["username"],
        "created_at": user["created_at"]
    }