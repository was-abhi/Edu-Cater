from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Edu-Cater API")

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


@app.get("/")
def root():
    return {"message": "Edu-Cater API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/test")
def test_api():
    return {
        "success": True,
        "message": "Frontend can communicate with Edu-Cater API"
    }