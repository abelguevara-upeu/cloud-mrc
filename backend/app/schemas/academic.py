from pydantic import BaseModel
from datetime import date
from typing import List, Optional

# --- Section Schemas ---
class SectionBase(BaseModel):
    name: str
    capacity: int = 30

class SectionCreate(SectionBase):
    grade_id: int

class Section(SectionBase):
    id: int
    grade_id: int

    class Config:
        from_attributes = True

# --- Grade Schemas ---
class GradeBase(BaseModel):
    name: str
    level: str # Primaria, Secundaria

class GradeCreate(GradeBase):
    pass

class Grade(GradeBase):
    id: int
    sections: List[Section] = []

    class Config:
        from_attributes = True

# --- Academic Year Schemas ---
class AcademicYearBase(BaseModel):
    year: int
    start_date: date
    end_date: date
    is_active: bool = False

class AcademicYearCreate(AcademicYearBase):
    pass

class AcademicYear(AcademicYearBase):
    id: int

    class Config:
        from_attributes = True
