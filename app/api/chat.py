import logging
import ssl

import httpx

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.gigachat_service import send_message


logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
async def chat(data: ChatRequest):
    try:
        answer = await send_message(data.message)

        return ChatResponse(response=answer)

    except httpx.HTTPStatusError as e:
        logger.error(
            "GigaChat HTTP error: status=%s",
            e.response.status_code,
        )

        raise HTTPException(
            status_code=502,
            detail="Ошибка HTTP при обращении к GigaChat",
        ) from e

    except (httpx.RequestError, ssl.SSLError) as e:
        logger.error(
            "GigaChat connection error: %s",
            type(e).__name__,
        )

        raise HTTPException(
            status_code=502,
            detail="Ошибка подключения к GigaChat",
        ) from e

    except (KeyError, ValueError) as e:
        logger.error(
            "GigaChat response parsing error: %s",
            type(e).__name__,
        )

        raise HTTPException(
            status_code=502,
            detail="Некорректный ответ GigaChat",
        ) from e