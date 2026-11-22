from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.emotion import router as emotion_router
from app.api.voice import router as voice_router
from app.config import settings

app = FastAPI(title="Psy Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.CORS_ORIGINS.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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