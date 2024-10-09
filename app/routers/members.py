from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from .. import schemas, crud, models
from ..database import get_db
from ..auth import get_current_active_librarian, get_current_active_member

router = APIRouter(
    prefix="/members",
    tags=["members"],
)

# Librarian Endpoints

# Add a new member
@router.post("/", response_model=schemas.UserResponse, dependencies=[Depends(get_current_active_librarian)])
async def create_member(member: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    if member.role.upper() != "MEMBER":
        raise HTTPException(status_code=400, detail="Can only create members")
    db_member = await crud.create_member(db, member)
    return db_member

# Update a member's details
@router.put("/{member_id}", response_model=schemas.UserResponse, dependencies=[Depends(get_current_active_librarian)])
async def update_member(member_id: int, member: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_member = await crud.update_member(db, member_id, member)
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member

# Delete a member (soft delete)
@router.delete("/{member_id}", response_model=schemas.UserResponse, dependencies=[Depends(get_current_active_librarian)])
async def delete_member(member_id: int, db: AsyncSession = Depends(get_db)):
    db_member = await crud.delete_member(db, member_id)
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member

# View all active members
@router.get("/", response_model=list[schemas.UserResponse], dependencies=[Depends(get_current_active_librarian)])
async def read_members(skip: int = 0, limit: int = 100, active: bool = True, db: AsyncSession = Depends(get_db)):
    members = await crud.get_members(db, skip=skip, limit=limit, active=active)
    return members

# View deleted members
@router.get("/deleted", response_model=list[schemas.UserResponse], dependencies=[Depends(get_current_active_librarian)])
async def read_deleted_members(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    members = await crud.get_members(db, skip=skip, limit=limit, active=False)
    return members

# View borrowing history of all members
@router.get("/history", response_model=list[schemas.HistoryResponse], dependencies=[Depends(get_current_active_librarian)])
async def read_members_history(db: AsyncSession = Depends(get_db)):
    db_history = await db.execute(
        db.query(models.History)
        .join(models.Book)
        .join(models.User)
    )
    history_records = db_history.scalars().all()
    return history_records


# Member Endpoints

# View own borrowing history
@router.get("/me/history", response_model=list[schemas.HistoryResponse], dependencies=[Depends(get_current_active_member)])
async def read_my_history(current_user: models.User = Depends(get_current_active_member), db: AsyncSession = Depends(get_db)):
    db_history = await db.execute(
        db.query(models.History)
        .join(models.Book)
        .filter(models.History.member_id == current_user.id)
    )
    history_records = db_history.scalars().all()
    return history_records

# Delete own account
@router.delete("/me", response_model=schemas.UserResponse, dependencies=[Depends(get_current_active_member)])
async def delete_own_account(current_user: models.User = Depends(get_current_active_member), db: AsyncSession = Depends(get_db)):
    db_user = await crud.delete_member(db, current_user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
