from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordRequestForm

import models, schemas, auth, database

# Initialize the router
router = APIRouter()

# User Token Verification
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    user = await auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Create a new user
@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Retrieve the current user's information
@router.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user


# Create a new book
@router.post("/books/", response_model=schemas.Book)
async def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    book_data = book.model_dump() 
    book_data["user_id"] = current_user.id 

    db_book = models.Book(**book_data)
    await db.add(db_book)
    await db.commit()
    await db.refresh(db_book)

    return db_book


# Get all books for the current user
@router.get("/books/", response_model=List[schemas.Book])
async def read_books(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    books = await db.query(models.Book).filter(models.Book.user_id == current_user.id).offset(skip).limit(limit).all()
    return books


# Get a specific book by id
@router.get("/books/{book_id}", response_model=schemas.Book)
async def read_book(book_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    book = await db.query(models.Book).filter(models.Book.id == book_id, models.Book.user_id == current_user.id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# Update a book by id
@router.put("/books/{book_id}", response_model=schemas.Book)
async def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_book = await db.query(models.Book).filter(models.Book.id == book_id, models.Book.user_id == current_user.id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book.model_dump().items():
        setattr(db_book, key, value)
    await db.commit()
    await db.refresh(db_book)
    return db_book


# Delete a book by id
@router.delete("/books/{book_id}", response_model=dict)
async def delete_book(book_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_book = await db.query(models.Book).filter(models.Book.id == book_id, models.Book.user_id == current_user.id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    await db.delete(db_book)
    await db.commit()
    return {"message": "Book deleted successfully"}
