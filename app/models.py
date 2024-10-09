# app/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'LIBRARIAN' or 'MEMBER'
    is_active = Column(Boolean, default=True)
    
    borrowed_books = relationship("Book", back_populates="borrower")
    history = relationship("History", back_populates="member")

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    status = Column(String, default="AVAILABLE")  # 'AVAILABLE' or 'BORROWED'
    borrower_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    borrower = relationship("User", back_populates="borrowed_books")
    history = relationship("History", back_populates="book")

class History(Base):
    __tablename__ = "history"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    member_id = Column(Integer, ForeignKey("users.id"))
    issue_date = Column(DateTime, default=datetime.utcnow)
    return_date = Column(DateTime, nullable=True)
    
    book = relationship("Book", back_populates="history")
    member = relationship("User", back_populates="history")
