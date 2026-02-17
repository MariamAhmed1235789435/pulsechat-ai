from sqlalchemy.orm import Session
from sqlalchemy import func, case
from . import models, schemas
from typing import Optional
from datetime import datetime, date


def create_lead(db: Session, lead: schemas.LeadCreate) -> models.Lead:
    db_lead = models.Lead(
        company_name=lead.company_name,
        phone=lead.phone,
        sector=lead.sector,
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


def get_leads(
    db: Session,
    status: Optional[str] = None,
    sector: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    query = db.query(models.Lead)

    if status:
        query = query.filter(models.Lead.status == status)
    if sector:
        query = query.filter(models.Lead.sector == sector)
    if search:
        query = query.filter(
            (models.Lead.company_name.contains(search))
            | (models.Lead.phone.contains(search))
        )

    total = query.count()
    leads = query.order_by(models.Lead.created_at.desc()).offset(offset).limit(limit).all()
    return leads, total


def get_lead(db: Session, lead_id: int) -> Optional[models.Lead]:
    return db.query(models.Lead).filter(models.Lead.id == lead_id).first()


def update_lead(db: Session, lead_id: int, lead_update: schemas.LeadUpdate) -> Optional[models.Lead]:
    db_lead = get_lead(db, lead_id)
    if not db_lead:
        return None

    if lead_update.status is not None:
        db_lead.status = lead_update.status
    if lead_update.notes is not None:
        db_lead.notes = lead_update.notes

    db.commit()
    db.refresh(db_lead)
    return db_lead


def delete_lead(db: Session, lead_id: int) -> bool:
    db_lead = get_lead(db, lead_id)
    if not db_lead:
        return False
    db.delete(db_lead)
    db.commit()
    return True


def get_analytics(db: Session) -> dict:
    total = db.query(models.Lead).count()

    today = date.today()
    today_count = db.query(models.Lead).filter(
        func.date(models.Lead.created_at) == today
    ).count()

    by_status = dict(
        db.query(models.Lead.status, func.count(models.Lead.id))
        .group_by(models.Lead.status)
        .all()
    )

    by_sector = dict(
        db.query(models.Lead.sector, func.count(models.Lead.id))
        .group_by(models.Lead.sector)
        .all()
    )

    converted = by_status.get("converted", 0)
    conversion_rate = round((converted / total * 100), 1) if total > 0 else 0

    top_sector = max(by_sector, key=by_sector.get) if by_sector else "-"

    return {
        "total": total,
        "today": today_count,
        "new": by_status.get("new", 0),
        "contacted": by_status.get("contacted", 0),
        "converted": converted,
        "rejected": by_status.get("rejected", 0),
        "conversion_rate": conversion_rate,
        "by_sector": by_sector,
        "by_status": by_status,
        "top_sector": top_sector,
    }
