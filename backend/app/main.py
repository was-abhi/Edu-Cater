from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.recommendations import router as recommendations_router
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine

app = FastAPI(title="Edu-Cater API")

#route for recc api
app.include_router(recommendations_router)

#middleware with frontend details
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#backend test
@app.get("/")
def root():
    return {"message": "Edu-Cater API is running"}

#health 
@app.get("/health")
def health():
    return {"status": "ok"}

#database connection test
@app.get("/health/database")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {"database": "connected"}

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        )

#Frontend communication test

@app.get("/api/v1/test")
def test_api():
    return {
        "success": True,
        "message": "Frontend can communicate with Edu-Cater API"
    }

@app.get("/api/v1/test")
def test_api():
    return {
        "success": True,
        "message": "Frontend can communicate with Edu-Cater API"
    }