from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.emotion import router as emotion_router
from app.api.voice import router as voice_router

app = FastAPI(title="Psy Assistant")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Psy Assistant API is running"}

app.include_router(
    emotion_router,
    prefix="/api/v1"
)
app.include_router(
    chat_router,
    prefix="/api/v1",
)
app.include_router(
    voice_router,
    prefix="/api/v1",
)