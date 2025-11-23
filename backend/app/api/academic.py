from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.academic import AcademicYear, Grade, Section
from app.schemas.academic import (
    AcademicYearCreate, AcademicYear as AcademicYearSchema,
    GradeCreate, Grade as GradeSchema,
    SectionCreate, Section as SectionSchema
)

router = APIRouter(dependencies=[Depends(get_current_user)])

# --- Academic Years ---
@router.post("/years", response_model=AcademicYearSchema)
def create_academic_year(year: AcademicYearCreate, db: Session = Depends(get_db)):
    db_year = db.query(AcademicYear).filter(AcademicYear.year == year.year).first()
    if db_year:
        raise HTTPException(status_code=400, detail="Año académico ya existe")
    
    new_year = AcademicYear(**year.model_dump())
    db.add(new_year)
    db.commit()
    db.refresh(new_year)
    return new_year

@router.get("/years", response_model=List[AcademicYearSchema])
def read_academic_years(db: Session = Depends(get_db)):
    return db.query(AcademicYear).all()

# --- Grades ---
@router.post("/grades", response_model=GradeSchema)
def create_grade(grade: GradeCreate, db: Session = Depends(get_db)):
    new_grade = Grade(**grade.model_dump())
    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)
    return new_grade

@router.get("/grades", response_model=List[GradeSchema])
def read_grades(db: Session = Depends(get_db)):
    return db.query(Grade).all()

# --- Sections ---
@router.post("/sections", response_model=SectionSchema)
def create_section(section: SectionCreate, db: Session = Depends(get_db)):
    # Verificar si el grado existe
    grade = db.query(Grade).filter(Grade.id == section.grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grado no encontrado")

    new_section = Section(**section.model_dump())
    db.add(new_section)
    db.commit()
    db.refresh(new_section)
    return new_section

@router.get("/sections", response_model=List[SectionSchema])
def read_sections(grade_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Section)
    if grade_id:
        query = query.filter(Section.grade_id == grade_id)
    return query.all()
