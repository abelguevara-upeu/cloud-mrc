from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentBase(BaseModel):
    type: str
    status: Optional[str] = "Pendiente"

class DocumentCreate(DocumentBase):
    enrollment_id: int
    file_url: str

class DocumentUpdate(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None
    file_url: Optional[str] = None

class Document(DocumentBase):
    id: int
    enrollment_id: int
    file_url: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
