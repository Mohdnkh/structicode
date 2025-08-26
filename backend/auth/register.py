from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import random
import requests

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

@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(password)
    verification_code = str(random.randint(100000, 999999))

    new_user = User(
        email=email,
        hashed_password=hashed_password,
        verification_code=verification_code,
        is_verified=False
    )
    db.add(new_user)
    db.commit()

    # إرسال الكود عبر Resend
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": "Bearer re_Kfz38sgr_MnQJXLz1i162Y8JGZJtvtsrr",
            "Content-Type": "application/json"
        },
        json={
            "from": "Structicode <onboarding@resend.dev>",
            "to": [email],
            "subject": "Your Verification Code",
            "html": f"<p>Your code is: <strong>{verification_code}</strong></p>"
        }
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to send verification email")

    return {"message": "Registration successful. Please check your email for the verification code."}
