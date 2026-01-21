import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import CarRecommendationRequest, ChatRequest, ChatResponse
from app.ai.agent import run_agent
from app.ai.memory import get_history, reset_memory
from app.recommendations import build_recommendations
from app.services.nhtsa_issues import get_complaints_and_recalls
from app.data.catalog import load_cars_with_meta

app = FastAPI()

# Allow local frontend/dev tools
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/recommend")
def recommend_car(request: CarRecommendationRequest) -> dict:
    return build_recommendations(request)


@app.get("/nhtsa/issues")
def nhtsa_issues(make: str, model: str, model_year: int) -> dict:
    return get_complaints_and_recalls(model_year, make, model)


@app.get("/")
def health() -> dict:
    catalog, using_mock, last_updated = load_cars_with_meta()
    return {
        "status": "ok",
        "catalog_size": len(catalog),
        "using_mock_data": using_mock,
        "catalog_last_updated": last_updated,
    }


@app.get("/models")
def list_models() -> dict:
    catalog, using_mock, last_updated = load_cars_with_meta()
    items = [
        {"make": c.get("make"), "model": c.get("model"), "year": c.get("year")}
        for c in catalog
    ]
    unique = {f"{i['make']}_{i['model']}_{i['year']}": i for i in items if i["make"] and i["model"] and i["year"]}
    return {
        "count": len(unique),
        "using_mock_data": using_mock,
        "catalog_last_updated": last_updated,
        "models": list(unique.values()),
    }


@app.post("/chat/message", response_model=ChatResponse)
def chat_message(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id or str(uuid.uuid4())
    try:
        response_text = run_agent(session_id, request.message)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return ChatResponse(
        session_id=session_id,
        message=response_text,
        history=get_history(session_id),
    )


@app.get("/chat/history/{session_id}")
def chat_history(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "history": get_history(session_id),
    }


@app.post("/chat/reset/{session_id}")
def chat_reset(session_id: str) -> dict:
    reset_memory(session_id)
    return {"status": "ok", "session_id": session_id}
