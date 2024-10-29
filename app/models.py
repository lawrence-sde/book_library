from sqlalchemy import Boolean, ForeignKey, Integer, Column, String, Date
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique= True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    books = relationship("Book", back_populates="owner")

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement= True)
    title = Column(String)
    author = Column(String)
    published_date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="books")

