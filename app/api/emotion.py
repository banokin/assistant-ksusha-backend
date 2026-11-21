import json
import logging

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.schemas.emotion import EmotionCreate, EmotionAnalysis
from app.services.emotion_service import analyze_emotion


logger = logging.getLogger("uvicorn.error")


router = APIRouter(
    prefix="/emotion",
    tags=["Emotion Diary"]
)


@router.post(
    "/analyze",
    response_model=EmotionAnalysis
)
async def analyze(data: EmotionCreate):

    try:
        return await analyze_emotion(data)

    except (
        httpx.HTTPError,
        json.JSONDecodeError,
        ValidationError,
        KeyError,
        ValueError,
    ) as error:
        logger.error("Emotion analysis error: %s", error)
        raise HTTPException(
            status_code=502,
            detail="Ошибка анализа эмоций"
        ) from error