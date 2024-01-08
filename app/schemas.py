from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    email: EmailStr

class UserCreate(User): 
    password: str

class UserCreateOut(User):
    access_count: int
     

class URL(BaseModel):
    url: str
     
class TextData(BaseModel):
    data: str
    
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None    
    
    
class Login(BaseModel):
    email: EmailStr
    password: str