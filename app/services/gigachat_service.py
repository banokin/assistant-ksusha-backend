import ssl
import uuid
from pathlib import Path

import httpx

from app.config import settings


AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
_CERTS_DIR = Path(__file__).resolve().parents[2] / "certs"


def gigachat_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    context.load_verify_locations(cafile=str(_CERTS_DIR / "russian_trusted_root_ca.cer"))
    context.load_verify_locations(cafile=str(_CERTS_DIR / "russian_trusted_sub_ca.cer"))
    return context


async def get_access_token() -> str:
    headers = {
        "Authorization": f"Basic {settings.GIGACHAT_AUTHORIZATION_KEY}",
        "RqUID": str(uuid.uuid4()),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "scope": settings.GIGACHAT_SCOPE
    }

    async with httpx.AsyncClient(timeout=30.0, verify=gigachat_ssl_context()) as client:
        response = await client.post(
            AUTH_URL,
            headers=headers,
            data=data,
        )

        print("OAuth status:", response.status_code)

        response.raise_for_status()

        result = response.json()

        print("OAuth response keys:", list(result.keys()))

        token = result.get("access_token")

        if not isinstance(token, str) or not token:
            raise ValueError("OAuth response missing access_token")

        return token

async def send_message(message: str) -> str:
    token = await get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": message,
            }
        ],
    }

    async with httpx.AsyncClient(timeout=60.0, verify=gigachat_ssl_context()) as client:
        response = await client.post(
            GIGACHAT_URL,
            headers=headers,
            json=payload,
        )

        print("GigaChat status:", response.status_code)

        response.raise_for_status()

        result = response.json()

        print("Response keys:", list(result.keys()))

        choices = result.get("choices")

        if not isinstance(choices, list) or not choices:
            raise ValueError("GigaChat response missing choices")

        answer = choices[0].get("message", {}).get("content")

        if not isinstance(answer, str):
            raise ValueError("GigaChat response missing message content")

        return answer