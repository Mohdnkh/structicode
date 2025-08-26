from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from backend.db.db import SessionLocal
from backend.db.models import User
from backend.auth.login import create_access_token  # لإرجاع توكن بعد التفعيل

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Schema
class VerifyRequest(BaseModel):
    email: EmailStr
    code: str

@router.post("/verify")
def verify_email(req: VerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        return {"message": "User already verified"}

    if user.verification_code != req.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # ✅ تفعيل الحساب
    user.is_verified = True
    user.verification_code = None
    db.commit()

    # ✅ إنشاء access_token بعد التفعيل
    access_token = create_access_token(data={"sub": user.email})
    return {
        "message": "Email verified successfully",
        "access_token": access_token,
        "token_type": "bearer"
    }
