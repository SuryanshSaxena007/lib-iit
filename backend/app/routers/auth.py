from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, crud
from ..database import get_db
from pydantic import BaseModel

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/signup", response_model=schemas.UserResponse)
async def signup(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    if user.role.upper() not in ["LIBRARIAN", "MEMBER"]:
        raise HTTPException(status_code=400, detail="Role must be LIBRARIAN or MEMBER")
    return await crud.create_user(db, user)

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_username(db, username=login_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not crud.verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Generate JWT token
    
    access_token = crud.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}