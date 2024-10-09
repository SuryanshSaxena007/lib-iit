from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from . import models, schemas
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

# CRUD for Users
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        password_hash=hashed_password,
        role=user.role.upper(),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# CRUD for Books
async def get_book(db: AsyncSession, book_id: int):
    result = await db.execute(select(models.Book).where(models.Book.id == book_id))
    return result.scalars().first()

async def get_books(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Book).offset(skip).limit(limit))
    return result.scalars().all()

async def create_book(db: AsyncSession, book: schemas.BookCreate):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

async def update_book(db: AsyncSession, book_id: int, book: schemas.BookUpdate):
    db_book = await get_book(db, book_id)
    if db_book:
        for key, value in book.dict(exclude_unset=True).items():
            setattr(db_book, key, value)
        db.add(db_book)
        await db.commit()
        await db.refresh(db_book)
    return db_book

async def delete_book(db: AsyncSession, book_id: int):
    db_book = await get_book(db, book_id)
    if db_book:
        await db.delete(db_book)
        await db.commit()
    return db_book

# CRUD for Members (Users with role MEMBER)
async def get_member(db: AsyncSession, member_id: int):
    result = await db.execute(select(models.User).where(models.User.id == member_id, models.User.role == "MEMBER"))
    return result.scalars().first()

async def get_members(db: AsyncSession, skip: int = 0, limit: int = 100, active: bool = True):
    result = await db.execute(select(models.User).where(models.User.role == "MEMBER", models.User.is_active == active).offset(skip).limit(limit))
    return result.scalars().all()

async def create_member(db: AsyncSession, user: schemas.UserCreate):
    user.role = "MEMBER"
    return await create_user(db, user)

async def update_member(db: AsyncSession, member_id: int, user: schemas.UserCreate):
    db_member = await get_member(db, member_id)
    if db_member:
        db_member.username = user.username
        if user.password:
            db_member.password_hash = get_password_hash(user.password)
        db_member.role = user.role.upper()
        db.add(db_member)
        await db.commit()
        await db.refresh(db_member)
    return db_member

async def delete_member(db: AsyncSession, member_id: int):
    db_member = await get_member(db, member_id)
    if db_member:
        db_member.is_active = False
        db.add(db_member)
        await db.commit()
    return db_member

# Borrow and Return Books
async def borrow_book(db: AsyncSession, book_id: int, member_id: int):
    db_book = await get_book(db, book_id)
    if db_book and db_book.status == "AVAILABLE":
        db_book.status = "BORROWED"
        db_book.borrower_id = member_id
        history = models.History(book_id=book_id, member_id=member_id, issue_date=datetime.utcnow())
        db.add(history)
        db.add(db_book)
        await db.commit()
        await db.refresh(db_book)
        return db_book
    return None

async def return_book(db: AsyncSession, book_id: int, member_id: int):
    db_book = await get_book(db, book_id)
    if db_book and db_book.status == "BORROWED" and db_book.borrower_id == member_id:
        db_book.status = "AVAILABLE"
        db_book.borrower_id = None
        # Update the latest history record
        result = await db.execute(
            select(models.History)
            .where(models.History.book_id == book_id, models.History.member_id == member_id, models.History.return_date == None)
            .order_by(models.History.issue_date.desc())
        )
        history = result.scalars().first()
        if history:
            history.return_date = datetime.utcnow()
            db.add(history)
        db.add(db_book)
        await db.commit()
        await db.refresh(db_book)
        return db_book
    return None
