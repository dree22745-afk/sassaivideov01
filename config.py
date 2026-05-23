import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./omni.db")
JWT_SECRET = os.getenv("JWT_SECRET", "omni-secret-key")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
ALLOWED_USERS = os.getenv("ALLOWED_USERS", "")
ADMIN_IDS = os.getenv("ADMIN_IDS", "admin")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 60