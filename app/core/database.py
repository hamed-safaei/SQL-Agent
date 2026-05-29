from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DB_SERVER = os.getenv("DB_SERVER")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")

APP_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_DATABASE}"

app_engine = create_engine(APP_DATABASE_URL,echo=True)
AppSessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=app_engine)
Base = declarative_base()

def get_app_db():
    db = AppSessionLocal()
    try:
        yield db
    finally:
        db.close()
