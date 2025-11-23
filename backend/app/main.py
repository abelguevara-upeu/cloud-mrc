from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.db.init_db import init_db
from app.api import auth, students, academic, enrollments, documents

# Crear tablas en la base de datos al iniciar
Base.metadata.create_all(bind=engine)

# Inicializar datos (crear admin)
db = SessionLocal()
init_db(db)
db.close()

app = FastAPI(
    title="Sistema de Matrícula - I.E. Mariscal Ramón Castilla",
    description="API para gestión de matrículas, estudiantes y documentos.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(auth.router, prefix="/api/v1", tags=["login"])
app.include_router(students.router, prefix="/api/v1/students", tags=["students"])
app.include_router(academic.router, prefix="/api/v1/academic", tags=["academic"])
app.include_router(enrollments.router, prefix="/api/v1/enrollments", tags=["enrollments"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])

# Configuración CORS (Permitir que el frontend Vue consuma la API)
origins = [
    "http://localhost:3000", # Frontend local
    "http://localhost:5173", # Vite default port
    "*" # En producción restringir esto
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API del Sistema de Matrícula MRC"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
