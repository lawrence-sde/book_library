from pydantic import BaseModel
from datetime import date  
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: int
    email: str
    is_active: bool

    class config:
        orm_mode = True

class BookBase(BaseModel):
    title: str
    author: str
    published_date: date

class BookCreate(BookBase):
    pass 

class Book(BookBase):
    id: int 

    class config:
        orm_mode = True