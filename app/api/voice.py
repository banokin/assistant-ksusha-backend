import logging

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.speech_service import transcribe_audio

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/voice", tags=["Voice"])


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    content_type = (file.content_type or "").split(";", 1)[0].strip().lower()
    if content_type not in (
        "audio/webm",
        "audio/wav",
        "audio/mpeg",
        "audio/mp4",
        "audio/x-m4a",
    ):
        raise HTTPException(
            status_code=400,
            detail="Неподдерживаемый формат аудио",
        )

    audio = await file.read(10 * 1024 * 1024 + 1)

    if len(audio) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Аудиофайл слишком большой",
        )

    if not audio:
        raise HTTPException(
            status_code=400,
            detail="Пустой аудиофайл",
        )

    try:
        text = await transcribe_audio(
            audio=audio,
            filename=file.filename or "recording.webm",
            content_type=content_type,
        )
    except Exception as exc:
        logger.error("Transcription error: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Ошибка транскрибации аудио",
        ) from exc

    return {"text": text}