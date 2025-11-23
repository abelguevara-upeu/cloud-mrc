from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EnrollmentBase(BaseModel):
    student_id: int
    academic_year_id: int
    grade_id: int
    section_id: int

class EnrollmentCreate(EnrollmentBase):
    pass

# Nested schemas for related data
class StudentBasic(BaseModel):
    id: int
    dni: str
    first_name: str
    last_name: str
    
    class Config:
        from_attributes = True

class GradeBasic(BaseModel):
    id: int
    name: str
    level: str
    
    class Config:
        from_attributes = True

class SectionBasic(BaseModel):
    id: int
    name: str
    capacity: int
    
    class Config:
        from_attributes = True

class Enrollment(EnrollmentBase):
    id: int
    status: str
    created_at: datetime
    student: Optional[StudentBasic] = None
    grade: Optional[GradeBasic] = None
    section: Optional[SectionBasic] = None

    class Config:
        from_attributes = True
