from pydantic import BaseModel, EmailStr
from typing import Optional

# Schemas para autenticación
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol: str

class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    estado: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

# Schemas para usuarios
class UserBase(BaseModel):
    nombre: str
    email: EmailStr
    rol: str
    estado: bool = True

class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    rol: Optional[str] = None
    password: Optional[str] = None
    estado: Optional[bool] = None