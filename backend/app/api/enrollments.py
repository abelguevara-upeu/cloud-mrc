from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.enrollment import Enrollment
from app.models.academic import Section, AcademicYear
from app.models.student import Student
from app.schemas.enrollment import EnrollmentCreate, Enrollment as EnrollmentSchema

router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/", response_model=EnrollmentSchema)
def create_enrollment(enrollment: EnrollmentCreate, db: Session = Depends(get_db)):
    # 1. Validar que el estudiante exista
    student = db.query(Student).filter(Student.id == enrollment.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # 2. Validar que el año académico exista y esté activo (opcional, por ahora solo existencia)
    year = db.query(AcademicYear).filter(AcademicYear.id == enrollment.academic_year_id).first()
    if not year:
        raise HTTPException(status_code=404, detail="Año académico no encontrado")

    # 3. Validar Sección y Vacantes
    section = db.query(Section).filter(Section.id == enrollment.section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Sección no encontrada")
    
    # Contar matriculados actuales en esa sección
    current_enrollments = db.query(Enrollment).filter(
        Enrollment.section_id == enrollment.section_id,
        Enrollment.academic_year_id == enrollment.academic_year_id,
        Enrollment.status != "Rechazado" # Contamos pendientes y aprobados
    ).count()

    if current_enrollments >= section.capacity:
        raise HTTPException(status_code=400, detail="No hay vacantes disponibles en esta sección")

    # 4. Verificar si ya está matriculado en ese año
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == enrollment.student_id,
        Enrollment.academic_year_id == enrollment.academic_year_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="El estudiante ya está matriculado en este año académico")

    # 5. Crear Matrícula
    new_enrollment = Enrollment(
        student_id=enrollment.student_id,
        academic_year_id=enrollment.academic_year_id,
        grade_id=enrollment.grade_id,
        section_id=enrollment.section_id,
        status="Matriculado"  # Estado por defecto al crear matrícula
    )
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return new_enrollment

@router.get("/", response_model=List[EnrollmentSchema])
def read_enrollments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    enrollments = db.query(Enrollment)\
        .options(
            joinedload(Enrollment.student),
            joinedload(Enrollment.grade),
            joinedload(Enrollment.section)
        )\
        .offset(skip)\
        .limit(limit)\
        .all()
    return enrollments

@router.patch("/{enrollment_id}/status")
def update_enrollment_status(enrollment_id: int, status: str, db: Session = Depends(get_db)):
    valid_statuses = ["Matriculado", "Pendiente", "Retirado", "Rechazado"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}")
    
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Matrícula no encontrada")
    
    enrollment.status = status
    db.commit()
    db.refresh(enrollment)
    return {"message": f"Estado actualizado a {status}", "enrollment": enrollment}

@router.delete("/{enrollment_id}")
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Matrícula no encontrada")
    
    db.delete(enrollment)
    db.commit()
    return {"message": "Matrícula eliminada exitosamente"}
