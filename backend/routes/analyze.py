from fastapi import APIRouter

from services.nlp_service import (
    analyze_text
)

router = APIRouter()


@router.post("/analyze")
def analyze(payload: dict):

    text = payload.get(
        "text",
        ""
    )

    result = analyze_text(text)

    return result