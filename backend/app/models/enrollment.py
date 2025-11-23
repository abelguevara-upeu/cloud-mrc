from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    grade_id = Column(Integer, ForeignKey("grades.id"))
    section_id = Column(Integer, ForeignKey("sections.id"))
    status = Column(String, default="Pendiente") # Pendiente, Aprobado, Rechazado
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    student = relationship("Student", back_populates="enrollments")
    academic_year = relationship("AcademicYear", back_populates="enrollments")
    grade = relationship("Grade", back_populates="enrollments")
    section = relationship("Section", back_populates="enrollments")
    documents = relationship("Document", back_populates="enrollment")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"))
    type = Column(String, nullable=False) # DNI, Certificado, etc.
    file_url = Column(String, nullable=False)
    status = Column(String, default="Pendiente") # Pendiente, Validado, Observado
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    enrollment = relationship("Enrollment", back_populates="documents")
