from fastapi import FastAPI

app = FastAPI(title="Edu-Cater API")


@app.get("/")
def root():
    return {"message": "Edu-Cater API is running"}