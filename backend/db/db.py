from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# SQLite database path
DATABASE_URL = "sqlite:///./users.db"

# إنشاء الاتصال بقاعدة البيانات
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# إنشاء جلسة التعامل مع قاعدة البيانات
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# استدعاء هذا لإنشاء الجداول أول مرة
def init_db():
    Base.metadata.create_all(bind=engine)
