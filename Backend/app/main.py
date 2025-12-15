from fastapi import FastAPI
from app.services.external_apis import get_age_guess

app = FastAPI()

@app.get("/")
def root() -> dict:
    return {"status": "ok", "message": "Car recommender backend running"}


@app.get("/age-guess")
def age_guess(name: str) -> dict:
    data = get_age_guess(name)

    return {
        "input_name": name, 
        "estimated_age": data.get("age"),
        "samples": data.get("count"),
    }
