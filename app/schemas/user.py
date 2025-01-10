from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    address: str
    comments: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        from_attributes = True
