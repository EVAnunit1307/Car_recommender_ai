from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root() -> dict:
    return {"status": "ok", "message": "Car recommender backend running"}
