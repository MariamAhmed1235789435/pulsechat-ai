from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


# --- Lead Schemas ---

class LeadCreate(BaseModel):
    company_name: str
    phone: str
    sector: str

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("اسم الشركة لازم يكون حرفين على الأقل")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        cleaned = v.strip().replace(" ", "").replace("-", "")
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError("رقم الهاتف غير صحيح")
        return cleaned

    @field_validator("sector")
    @classmethod
    def validate_sector(cls, v):
        valid_sectors = [
            "pharmacy", "restaurant", "clinic", "ecommerce",
            "tourism", "services", "education", "realestate",
            "maintenance", "other"
        ]
        if v not in valid_sectors:
            raise ValueError("القطاع غير صحيح")
        return v


class LeadUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in ["new", "contacted", "converted", "rejected"]:
            raise ValueError("الحالة غير صحيحة")
        return v


class LeadResponse(BaseModel):
    id: int
    company_name: str
    phone: str
    sector: str
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Auth Schemas ---

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
