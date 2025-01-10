from sqlalchemy import Column, Integer, String, Text
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    address = Column(String)
    comments = Column(Text)
