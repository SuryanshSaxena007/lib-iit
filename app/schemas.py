from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: str  # 'LIBRARIAN' or 'MEMBER'

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        from_attributes = True  

# Book Schemas
class BookBase(BaseModel):
    title: str
    author: str

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    status: Optional[str] = None  # 'AVAILABLE' or 'BORROWED'

class BookResponse(BookBase):
    id: int
    status: str
    borrower_id: Optional[int]

    class Config:
        from_attributes = True  

# History Schemas
class HistoryResponse(BaseModel):
    id: int
    book_id: int
    member_id: int
    issue_date: datetime
    return_date: Optional[datetime]

    class Config:
        from_attributes = True  
    
# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
