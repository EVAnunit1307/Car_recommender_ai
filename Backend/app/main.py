from fastapi import FastAPI
from app.services.external_apis import get_age_guess
from app.models import AgeGuessRequest
from app.models import CarRecommendationRequest
from app.services.nhtsa_issues import get_complaints_and_recalls
app = FastAPI()


@app.post("/recommend")
def recommend_car(request: CarRecommendationRequest) -> dict:
    return {
        "message": "Recommendation logic not implemented yet",
        "input_received": request.dict()
    }



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

@app.get("/nhtsa/issues")
def nhtsa_issues(make: str, model: str, model_year: int) -> dict:
    return get_complaints_and_recalls(model_year, make, model)
