import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    DB_SERVER = os.getenv("DB_SERVER", "")
    DB_DATABASE = os.getenv("DB_DATABASE", "")
    DB_USER = os.getenv("PG_USER", "")
    DB_PASSWORD = os.getenv("PG_PASSWORD", "")
    DB_PORT = os.getenv("PG_PORT", "")
    


settings = Settings()