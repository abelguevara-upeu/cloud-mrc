from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class AcademicYear(Base):
    __tablename__ = "academic_years"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=False)
    
    enrollments = relationship("Enrollment", back_populates="academic_year")

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # 1ro, 2do...
    level = Column(String, nullable=False) # Primaria, Secundaria
    
    sections = relationship("Section", back_populates="grade")
    enrollments = relationship("Enrollment", back_populates="grade")

class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # A, B, C...
    grade_id = Column(Integer, ForeignKey("grades.id"))
    capacity = Column(Integer, default=30)
    
    grade = relationship("Grade", back_populates="sections")
    enrollments = relationship("Enrollment", back_populates="section")
