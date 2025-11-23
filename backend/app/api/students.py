from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.student import Student, Guardian
from app.schemas.student import StudentCreate, Student as StudentSchema, GuardianCreate

router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/", response_model=StudentSchema)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    # 1. Buscar si el apoderado existe por DNI
    db_guardian = db.query(Guardian).filter(Guardian.dni == student.guardian_dni).first()
    
    if not db_guardian:
        # En un flujo real, deberíamos pedir datos del apoderado si no existe.
        # Por simplicidad ahora, si no existe lanzamos error pidiendo crearlo antes.
        raise HTTPException(status_code=404, detail="Apoderado no encontrado. Registre al apoderado primero.")

    # 2. Verificar si estudiante ya existe
    db_student = db.query(Student).filter(Student.dni == student.dni).first()
    if db_student:
        raise HTTPException(status_code=400, detail="Estudiante ya registrado")

    # 3. Crear estudiante
    new_student = Student(
        dni=student.dni,
        first_name=student.first_name,
        last_name=student.last_name,
        birth_date=student.birth_date,
        address=student.address,
        guardian_id=db_guardian.id
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@router.get("/", response_model=List[StudentSchema])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    students = db.query(Student).options(joinedload(Student.guardian)).offset(skip).limit(limit).all()
    return students

# --- Endpoints de apoderados (ANTES de las rutas con parámetros dinámicos) ---
@router.get("/guardian", response_model=List[GuardianCreate])
def read_guardians(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    guardians = db.query(Guardian).offset(skip).limit(limit).all()
    return guardians

@router.post("/guardian", response_model=GuardianCreate)
def create_guardian(guardian: GuardianCreate, db: Session = Depends(get_db)):
    db_guardian = db.query(Guardian).filter(Guardian.dni == guardian.dni).first()
    if db_guardian:
        raise HTTPException(status_code=400, detail="Apoderado ya registrado")
    
    new_guardian = Guardian(**guardian.model_dump())
    db.add(new_guardian)
    db.commit()
    db.refresh(new_guardian)
    return new_guardian

@router.put("/guardian/{dni}", response_model=GuardianCreate)
def update_guardian(dni: str, guardian: GuardianCreate, db: Session = Depends(get_db)):
    db_guardian = db.query(Guardian).filter(Guardian.dni == dni).first()
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")
    
    # Actualizar datos
    db_guardian.dni = guardian.dni
    db_guardian.first_name = guardian.first_name
    db_guardian.last_name = guardian.last_name
    db_guardian.phone = guardian.phone
    db_guardian.email = guardian.email
    
    db.commit()
    db.refresh(db_guardian)
    return db_guardian

@router.delete("/guardian/{dni}")
def delete_guardian(dni: str, db: Session = Depends(get_db)):
    guardian = db.query(Guardian).filter(Guardian.dni == dni).first()
    if not guardian:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")
    
    # Verificar si tiene estudiantes asociados
    students_count = db.query(Student).filter(Student.guardian_id == guardian.id).count()
    if students_count > 0:
        raise HTTPException(status_code=400, detail=f"No se puede eliminar. Tiene {students_count} estudiante(s) asociado(s)")
    
    db.delete(guardian)
    db.commit()
    return {"message": "Apoderado eliminado exitosamente"}

# --- Rutas con parámetros dinámicos AL FINAL ---
@router.get("/{dni}", response_model=StudentSchema)
def read_student_by_dni(dni: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.dni == dni).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return student

@router.put("/{student_id}", response_model=StudentSchema)
def update_student(student_id: int, student: StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # Verificar que el apoderado existe
    db_guardian = db.query(Guardian).filter(Guardian.dni == student.guardian_dni).first()
    if not db_guardian:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")
    
    # Actualizar datos
    db_student.dni = student.dni
    db_student.first_name = student.first_name
    db_student.last_name = student.last_name
    db_student.birth_date = student.birth_date
    db_student.address = student.address
    db_student.guardian_id = db_guardian.id
    
    db.commit()
    db.refresh(db_student)
    return db_student

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # Verificar si tiene matrículas
    from app.models.enrollment import Enrollment
    enrollments_count = db.query(Enrollment).filter(Enrollment.student_id == student_id).count()
    if enrollments_count > 0:
        raise HTTPException(status_code=400, detail=f"No se puede eliminar. Tiene {enrollments_count} matrícula(s) registrada(s)")
    
    db.delete(student)
    db.commit()
    return {"message": "Estudiante eliminado exitosamente"}
