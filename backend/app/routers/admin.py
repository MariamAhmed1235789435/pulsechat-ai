from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import io
import csv

from .. import schemas, crud
from ..database import get_db

router = APIRouter(tags=["admin"])

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECTOR_LABELS = {
    "pharmacy": "صيدلية",
    "restaurant": "مطعم",
    "clinic": "عيادة / مستشفى",
    "ecommerce": "متجر إلكتروني",
    "tourism": "سياحة",
    "services": "خدمات مهنية",
    "education": "مراكز تعليمية",
    "realestate": "عقارات",
    "maintenance": "خدمات صيانة",
    "other": "أخرى",
}

STATUS_LABELS = {
    "new": "جديد",
    "contacted": "تم التواصل",
    "converted": "تم التحويل",
    "rejected": "مرفوض",
}


def create_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="غير مصرح")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="غير مصرح")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="انتهت صلاحية الجلسة")


# --- Auth ---

@router.post("/api/admin/login")
def login(data: schemas.LoginRequest, response: Response):
    if data.username != ADMIN_USERNAME or data.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="بيانات الدخول غير صحيحة")

    token = create_token(data.username)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=86400,
        samesite="lax",
    )
    return {"success": True, "message": "تم تسجيل الدخول"}


@router.post("/api/admin/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"success": True}


# --- Admin API ---

@router.get("/api/admin/leads")
def list_leads(
    status: str = None,
    sector: str = None,
    search: str = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    _user: str = Depends(verify_token),
):
    leads, total = crud.get_leads(db, status=status, sector=sector, search=search, limit=limit, offset=offset)
    return {
        "leads": [schemas.LeadResponse.model_validate(l) for l in leads],
        "total": total,
    }


@router.patch("/api/admin/leads/{lead_id}")
def update_lead(
    lead_id: int,
    data: schemas.LeadUpdate,
    db: Session = Depends(get_db),
    _user: str = Depends(verify_token),
):
    lead = crud.update_lead(db, lead_id, data)
    if not lead:
        raise HTTPException(status_code=404, detail="العميل غير موجود")
    return {"success": True, "lead": schemas.LeadResponse.model_validate(lead)}


@router.delete("/api/admin/leads/{lead_id}")
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    _user: str = Depends(verify_token),
):
    if not crud.delete_lead(db, lead_id):
        raise HTTPException(status_code=404, detail="العميل غير موجود")
    return {"success": True}


@router.get("/api/admin/analytics")
def analytics(
    db: Session = Depends(get_db),
    _user: str = Depends(verify_token),
):
    return crud.get_analytics(db)


@router.get("/api/admin/export")
def export_csv(
    db: Session = Depends(get_db),
    _user: str = Depends(verify_token),
):
    leads, _ = crud.get_leads(db, limit=10000)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Company", "Phone", "Sector", "Status", "Notes", "Created"])

    for lead in leads:
        writer.writerow([
            lead.id,
            lead.company_name,
            lead.phone,
            SECTOR_LABELS.get(lead.sector, lead.sector),
            STATUS_LABELS.get(lead.status, lead.status),
            lead.notes or "",
            lead.created_at.strftime("%Y-%m-%d %H:%M") if lead.created_at else "",
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"},
    )


# --- Admin Dashboard Pages ---

@router.get("/admin/login", response_class=HTMLResponse)
def login_page(request: Request):
    from ..main import templates
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/admin", response_class=HTMLResponse)
def dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
):
    # Check auth via cookie
    token = request.cookies.get("access_token")
    if not token:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/admin/login")
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/admin/login")

    stats = crud.get_analytics(db)
    leads, total = crud.get_leads(db, limit=100)

    from ..main import templates
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "leads": leads,
        "total": total,
        "sector_labels": SECTOR_LABELS,
        "status_labels": STATUS_LABELS,
    })
