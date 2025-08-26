from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import random
import requests
from pydantic import BaseModel, EmailStr

from backend.db.db import SessionLocal
from backend.db.models import User

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Pydantic schema
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
def signup(req: SignUpRequest, db: Session = Depends(get_db)):
    # تحقق إذا المستخدم موجود
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # تشفير الباسورد
    hashed_password = pwd_context.hash(req.password)
    verification_code = str(random.randint(100000, 999999))

    # إنشاء المستخدم
    new_user = User(
        email=req.email,
        hashed_password=hashed_password,
        verification_code=verification_code,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # إرسال الكود عبر Resend
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {os.getenv('RESEND_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "from": "Structicode <onboarding@resend.dev>",
            "to": [req.email],
            "subject": "Your Verification Code",
            "html": f"<p>Your code is: <strong>{verification_code}</strong></p>"
        }
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to send verification email")

    return {
        "message": "Registration successful. Please check your email for the verification code.",
        "email": req.email
    }
