from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, List

# --- Guardian Schemas ---
class GuardianBase(BaseModel):
    dni: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class GuardianCreate(GuardianBase):
    pass

class Guardian(GuardianBase):
    id: int
    
    class Config:
        from_attributes = True

# --- Student Schemas ---
class StudentBase(BaseModel):
    dni: str
    first_name: str
    last_name: str
    birth_date: date
    address: Optional[str] = None

class StudentCreate(StudentBase):
    guardian_dni: str # Para vincular con apoderado existente o crear uno nuevo

class Student(StudentBase):
    id: int
    guardian_id: int
    guardian: Optional[Guardian] = None

    class Config:
        from_attributes = True
