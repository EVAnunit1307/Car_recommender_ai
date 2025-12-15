from fastapi import FastAPI
from app.services.external_apis import get_age_guess
from app.models import AgeGuessRequest

app = FastAPI()

@app.get("/")
def root() -> dict:
    return {"status": "ok", "message": "Car recommender backend running"}


@app.post("/age-guess")
def age_guess_post(payload: AgeGuessRequest) -> dict:
    data = get_age_guess(payload.name)

    if "error" in data:
        return {"input_name": payload.name, "error": data["error"]}

    return {
        "input_name": payload.name,
        "estimated_age": data.get("age"),
        "samples": data.get("count"),
    }