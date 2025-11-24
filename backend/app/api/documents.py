from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api import deps
from app.models.enrollment import Document, Enrollment
from app.schemas.document import Document as DocumentSchema, DocumentCreate, DocumentUpdate
import os
import shutil
from pathlib import Path
from datetime import datetime

router = APIRouter()

# Directorio para almacenar archivos
UPLOAD_DIR = Path("uploads/documents")

def ensure_upload_dir():
    """Crear directorio de uploads si no existe"""
    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create upload directory: {e}")

@router.get("/", response_model=List[DocumentSchema])
def get_documents(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    enrollment_id: Optional[int] = None,
    current_user: dict = Depends(deps.get_current_user)
):
    """Obtener lista de documentos, opcionalmente filtrados por matrícula"""
    query = db.query(Document)
    
    if enrollment_id:
        query = query.filter(Document.enrollment_id == enrollment_id)
    
    documents = query.offset(skip).limit(limit).all()
    return documents

@router.get("/{document_id}", response_model=DocumentSchema)
def get_document(
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Obtener un documento específico"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return document

@router.post("/upload", response_model=DocumentSchema)
async def upload_document(
    enrollment_id: int = Form(...),
    type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Subir un documento para una matrícula"""
    # Asegurar que el directorio existe antes de subir
    ensure_upload_dir()
    
    # Verificar que la matrícula existe
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Matrícula no encontrada")
    
    # Validar extensión de archivo
    allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de archivo no permitido. Permitidos: {', '.join(allowed_extensions)}"
        )
    
    # Generar nombre único para el archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{enrollment_id}_{type}_{timestamp}{file_ext}"
    file_path = UPLOAD_DIR / safe_filename
    
    # Guardar archivo
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar archivo: {str(e)}")
    
    # Crear registro en BD
    db_document = Document(
        enrollment_id=enrollment_id,
        type=type,
        file_url=str(file_path),
        status="Pendiente"
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

@router.patch("/{document_id}/status", response_model=DocumentSchema)
def update_document_status(
    document_id: int,
    status: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Actualizar el estado de un documento (Pendiente, Validado, Observado)"""
    valid_statuses = ["Pendiente", "Validado", "Observado"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Permitidos: {', '.join(valid_statuses)}")
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    document.status = status
    db.commit()
    db.refresh(document)
    
    return document

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Eliminar un documento"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    # Eliminar archivo físico
    try:
        file_path = Path(document.file_url)
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"Error al eliminar archivo: {e}")
    
    db.delete(document)
    db.commit()
    
    return {"message": "Documento eliminado correctamente"}
