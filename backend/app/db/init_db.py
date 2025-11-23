from sqlalchemy.orm import Session
from app.models.user import User
from app.models.academic import AcademicYear, Grade, Section
from app.core.security import get_password_hash
from datetime import date

def init_db(db: Session) -> None:
    # Crear superusuario si no existe
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        user = User(
            username="admin",
            email="admin@mrc.edu.pe",
            hashed_password=get_password_hash("admin123"),
            full_name="Administrador Sistema",
            role="admin",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("✓ Usuario 'admin' creado con password 'admin123'")
    else:
        print("✓ Usuario 'admin' ya existe")
    
    # Crear años académicos
    years_data = [
        {"year": 2024, "start_date": date(2024, 3, 1), "end_date": date(2024, 12, 20), "is_active": False},
        {"year": 2025, "start_date": date(2025, 3, 1), "end_date": date(2025, 12, 20), "is_active": True},
        {"year": 2026, "start_date": date(2026, 3, 1), "end_date": date(2026, 12, 20), "is_active": False},
    ]
    
    for year_data in years_data:
        year = db.query(AcademicYear).filter(AcademicYear.year == year_data["year"]).first()
        if not year:
            year = AcademicYear(**year_data)
            db.add(year)
            print(f"✓ Año académico {year_data['year']} creado")
    
    db.commit()
    
    # Crear grados (Primaria y Secundaria)
    grades_data = [
        {"name": "1° Primaria", "level": "Primaria"},
        {"name": "2° Primaria", "level": "Primaria"},
        {"name": "3° Primaria", "level": "Primaria"},
        {"name": "4° Primaria", "level": "Primaria"},
        {"name": "5° Primaria", "level": "Primaria"},
        {"name": "6° Primaria", "level": "Primaria"},
        {"name": "1° Secundaria", "level": "Secundaria"},
        {"name": "2° Secundaria", "level": "Secundaria"},
        {"name": "3° Secundaria", "level": "Secundaria"},
        {"name": "4° Secundaria", "level": "Secundaria"},
        {"name": "5° Secundaria", "level": "Secundaria"},
    ]
    
    created_grades = []
    for grade_data in grades_data:
        grade = db.query(Grade).filter(Grade.name == grade_data["name"]).first()
        if not grade:
            grade = Grade(**grade_data)
            db.add(grade)
            db.flush()
            created_grades.append(grade)
            print(f"✓ Grado '{grade_data['name']}' creado")
        else:
            created_grades.append(grade)
    
    db.commit()
    
    # Crear secciones para cada grado
    sections_letters = ["A", "B", "C"]
    section_count = 0
    
    all_grades = db.query(Grade).all()
    for grade in all_grades:
        for letter in sections_letters:
            section_name = f"{grade.name} - Sección {letter}"
            section = db.query(Section).filter(
                Section.grade_id == grade.id,
                Section.name == letter
            ).first()
            
            if not section:
                # Capacidad según nivel: Primaria 30, Secundaria 35
                capacity = 30 if "Primaria" in grade.name else 35
                section = Section(
                    name=letter,
                    grade_id=grade.id,
                    capacity=capacity
                )
                db.add(section)
                section_count += 1
    
    db.commit()
    if section_count > 0:
        print(f"✓ {section_count} secciones creadas")
    
    print("=" * 50)
    print("✓ Base de datos inicializada correctamente")
    print("=" * 50)
