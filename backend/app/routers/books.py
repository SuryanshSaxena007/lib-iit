from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from .. import schemas, crud, models
from ..database import get_db
from ..auth import get_current_active_librarian, get_current_active_member
from datetime import datetime
from typing import List

router = APIRouter(
    prefix="/books",
    tags=["books"],
)

# Librarian Endpoints

# Add a new book
@router.post("/", response_model=schemas.BookResponse, dependencies=[Depends(get_current_active_librarian)])
async def create_book(book: schemas.BookCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_book(db, book)

# Update an existing book
@router.put("/{book_id}", response_model=schemas.BookResponse, dependencies=[Depends(get_current_active_librarian)])
async def update_book(book_id: int, book: schemas.BookUpdate, db: AsyncSession = Depends(get_db)):
    db_book = await crud.update_book(db, book_id, book)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

# Delete a book
@router.delete("/{book_id}", response_model=schemas.BookResponse, dependencies=[Depends(get_current_active_librarian)])
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    db_book = await crud.delete_book(db, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

# View all books
@router.get("/", response_model=List[schemas.BookResponse])
async def read_books(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    books = await crud.get_books(db, skip=skip, limit=limit)
    return books

# Member Endpoints

# View available books (those that are not borrowed)
@router.get("/available", response_model=List[schemas.BookResponse], dependencies=[Depends(get_current_active_member)])
async def read_available_books(db: AsyncSession = Depends(get_db)):
    db_books = await db.execute(
        db.query(models.Book)
        .filter(models.Book.status == "AVAILABLE")
    )
    available_books = db_books.scalars().all()
    return available_books

# Borrow a book
@router.post("/borrow/{book_id}", response_model=schemas.BookResponse, dependencies=[Depends(get_current_active_member)])
async def borrow_book(book_id: int, current_user: models.User = Depends(get_current_active_member), db: AsyncSession = Depends(get_db)):
    db_book = await db.get(models.Book, book_id)
    
    if db_book and db_book.status == "AVAILABLE":
        db_book.status = "BORROWED"
        db_book.borrower_id = current_user.id
        
        # Create a history entry
        history = models.History(book_id=db_book.id, member_id=current_user.id, issue_date=datetime.utcnow())
        db.add(history)
        db.add(db_book)
        await db.commit()
        await db.refresh(db_book)
        
        return db_book
    else:
        raise HTTPException(status_code=400, detail="Book not available for borrowing")

# Return a book
@router.post("/return/{book_id}", response_model=schemas.BookResponse, dependencies=[Depends(get_current_active_member)])
async def return_book(book_id: int, current_user: models.User = Depends(get_current_active_member), db: AsyncSession = Depends(get_db)):
    db_book = await db.get(models.Book, book_id)
    
    if db_book and db_book.status == "BORROWED" and db_book.borrower_id == current_user.id:
        db_book.status = "AVAILABLE"
        db_book.borrower_id = None

        # Find the latest history record using join
        db_history = await db.execute(
            db.query(models.History)
            .join(models.Book)
            .filter(models.History.book_id == db_book.id)
            .filter(models.History.member_id == current_user.id)
            .filter(models.History.return_date.is_(None))
        )
        history_record = db_history.scalars().first()
        
        # Update the return date
        if history_record:
            history_record.return_date = datetime.utcnow()
            db.add(history_record)
        
        db.add(db_book)
        await db.commit()
        await db.refresh(db_book)
        
        return db_book
    else:
        raise HTTPException(status_code=400, detail="You cannot return a book that is not borrowed by you")
