import httpx

from app.services.gigachat_service import get_access_token, gigachat_ssl_context


FILES_URL = "https://gigachat.devices.sberbank.ru/api/v1/files"
CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"


async def transcribe_audio(
    audio: bytes,
    filename: str,
    content_type: str,
) -> str:

    token = await get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with httpx.AsyncClient(
        timeout=120.0,
        verify=gigachat_ssl_context(),
    ) as client:

        # 1. Загружаем аудиофайл
        upload_response = await client.post(
            FILES_URL,
            headers=headers,
            files={
                "file": (
                    filename,
                    audio,
                    content_type,
                )
            },
            data={
                "purpose": "general"
            },
        )

        if upload_response.is_error:
            raise ValueError(_error_message(upload_response))

        file_id = upload_response.json()["id"]

        # 2. Отправляем аудио модели
        payload = {
            "model": "GigaChat-2-Pro",
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Транскрибируй аудиозапись "
                        "максимально дословно на языке оригинала. "
                        "Верни только текст речи без пояснений. "
                        "Не добавляй слов, которых нет в записи."
                    ),
                    "attachments": [file_id],
                }
            ],
        }

        response = await client.post(
            CHAT_URL,
            headers=headers,
            json=payload,
        )

        if response.is_error:
            raise ValueError(_error_message(response))

        result = response.json()

        return result["choices"][0]["message"]["content"]


def _error_message(response: httpx.Response) -> str:
    try:
        message = response.json().get("message")
    except ValueError:
        message = None
    return message or response.text or f"HTTP {response.status_code}"