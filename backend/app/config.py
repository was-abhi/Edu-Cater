import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ML_SERVER_URL = os.getenv("ML_SERVER_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")