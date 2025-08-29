from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import random
import requests
import os
from pydantic import BaseModel, EmailStr

from backend.db.db import SessionLocal
from backend.db.models import User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Schema
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
def signup(req: SignUpRequest, db: Session = Depends(get_db)):
    # تحقق إذا الإيميل موجود
    existing_user = db.query(User).filter(User.email == req.email).first()

    # إذا المستخدم موجود ومفعل → Error
    if existing_user and existing_user.is_verified:
        raise HTTPException(status_code=400, detail="Email already registered")

    # إذا المستخدم موجود لكن مش مفعل → نحدث الباسورد ونبعت كود جديد
    if existing_user and not existing_user.is_verified:
        existing_user.hashed_password = pwd_context.hash(req.password)
        existing_user.verification_code = str(random.randint(100000, 999999))
        db.commit()
        db.refresh(existing_user)
        target_email = existing_user.email
        verification_code = existing_user.verification_code
    else:
        # مستخدم جديد
        hashed_password = pwd_context.hash(req.password)
        verification_code = str(random.randint(100000, 999999))

        new_user = User(
            email=req.email,
            hashed_password=hashed_password,
            verification_code=verification_code,
            is_verified=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        target_email = new_user.email

    # إرسال الكود عبر Resend
    resend_api_key = os.getenv("RESEND_API_KEY")
    if not resend_api_key:
        raise HTTPException(status_code=500, detail="Email service not configured")

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json"
        },
        json={
            "from": "Structicode <onboarding@resend.dev>",
            "to": [target_email],
            "subject": "Your Verification Code",
            "html": f"<p>Your code is: <strong>{verification_code}</strong></p>"
        }
    )

    if response.status_code not in [200, 202]:
        # نطبع السبب باللوج عشان تقدر تشوفه بالـ Railway logs
        print("❌ Resend error:", response.status_code, response.text)
        raise HTTPException(status_code=500, detail="Failed to send verification email")

    return {
        "message": "Registration successful. Please check your email for the verification code.",
        "email": target_email
    }
