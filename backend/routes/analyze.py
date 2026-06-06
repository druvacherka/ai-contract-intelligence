from fastapi import APIRouter

router = APIRouter()

@router.post("/analyze")
def analyze(payload: dict):

    return {
        "message": "Analyze endpoint ready",
        "payload": payload
    }