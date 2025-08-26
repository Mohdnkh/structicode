from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.db.db import SessionLocal
from backend.db.models import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/verify")
def verify_email(email: str, code: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        return {"message": "User already verified"}

    if user.verification_code != code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    user.is_verified = True
    user.verification_code = None  # نلغي الكود بعد الاستخدام
    db.commit()

    return {"message": "Email verified successfully"}
