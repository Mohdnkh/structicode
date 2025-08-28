from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# ✅ رابط قاعدة البيانات (من env أو SQLite افتراضي للتجارب)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# ✅ إنشاء محرك قاعدة البيانات
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# ✅ جلسة للتعامل مع قاعدة البيانات
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Base لجميع الموديلات
Base = declarative_base()

# ✅ إنشاء الجداول عند أول تشغيل
def init_db():
    from backend.db import models  # استيراد الموديلات
    Base.metadata.create_all(bind=engine)
