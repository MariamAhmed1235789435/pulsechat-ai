from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.post("/")
def submit_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    db_lead = crud.create_lead(db, lead)
    return {
        "success": True,
        "message": "تم استلام طلبك بنجاح! سنتواصل معك قريباً.",
        "id": db_lead.id,
    }
