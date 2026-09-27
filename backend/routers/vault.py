import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from security import require_auth

router = APIRouter(prefix="/api/vault", tags=["Document Vault"])

def compute_document_status(expiry_date_str: str) -> str:
    try:
        expiry = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        if expiry < today:
            return "expired"
        elif (expiry - today).days <= 30:
            return "expiring_soon"
        else:
            return "valid"
    except Exception:
        return "valid"

@router.get("/documents", response_model=List[schemas.DocumentOut])
def get_user_documents(user: models.User = Depends(require_auth), db: Session = Depends(get_db)):
    docs = db.query(models.Document).filter(models.Document.user_id == user.id).all()
    # Recalculate status dynamically
    for d in docs:
        d.status = compute_document_status(d.expiry_date)
    db.commit()
    return docs

@router.post("/documents", response_model=schemas.DocumentOut)
def upload_document(
    payload: schemas.DocumentUpload,
    user: models.User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    status_calculated = compute_document_status(payload.expiry_date)

    doc = models.Document(
        user_id=user.id,
        document_type=payload.document_type,
        document_name=payload.document_name,
        document_number=payload.document_number,
        expiry_date=payload.expiry_date,
        file_type=payload.file_type or "pdf",
        file_size_kb=payload.file_size_kb or 120,
        file_content_base64=payload.file_content_base64,
        status=status_calculated
    )
    db.add(doc)

    audit = models.AuditLog(
        user_id=user.id,
        action="DOCUMENT_UPLOADED",
        details=f"Type: {payload.document_type}, Name: {payload.document_name}"
    )
    db.add(audit)
    db.commit()
    db.refresh(doc)
    return doc

@router.get("/documents/{doc_id}")
def get_document_content(
    doc_id: int,
    user: models.User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    doc = db.query(models.Document).filter(
        models.Document.id == doc_id,
        models.Document.user_id == user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found or access denied.")

    return {
        "id": doc.id,
        "document_type": doc.document_type,
        "document_name": doc.document_name,
        "document_number": doc.document_number,
        "expiry_date": doc.expiry_date,
        "file_type": doc.file_type,
        "file_content_base64": doc.file_content_base64,
        "status": compute_document_status(doc.expiry_date)
    }

@router.delete("/documents/{doc_id}")
def delete_document(
    doc_id: int,
    user: models.User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    doc = db.query(models.Document).filter(
        models.Document.id == doc_id,
        models.Document.user_id == user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    db.delete(doc)
    audit = models.AuditLog(
        user_id=user.id,
        action="DOCUMENT_DELETED",
        details=f"Doc ID: {doc_id}, Type: {doc.document_type}"
    )
    db.add(audit)
    db.commit()
    return {"message": "Document securely removed from vault."}
