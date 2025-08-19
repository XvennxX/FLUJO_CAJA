from pydantic import BaseModel, Field
from typing import Optional

class CompaniaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la compañía")

class CompaniaCreate(CompaniaBase):
    pass

class CompaniaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre de la compañía")

class CompaniaResponse(CompaniaBase):
    id: int

    class Config:
        from_attributes = True

class CompaniaListResponse(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True
