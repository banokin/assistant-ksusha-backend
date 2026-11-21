import json
import re

from app.schemas.emotion import EmotionCreate, EmotionAnalysis
from app.services.gigachat_service import send_message


def _extract_json(text: str) -> dict:
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        cleaned = fenced.group(1).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("В ответе GigaChat нет JSON-объекта")

    payload = json.loads(cleaned[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("Ответ GigaChat должен быть JSON-объектом")
    return payload


def _normalize_distortions(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        raise ValueError("cognitive_distortions должен быть списком")

    result: list[str] = []
    for item in value:
        if isinstance(item, str):
            text = item.strip()
        elif isinstance(item, dict):
            title = ""
            for key in ("name", "title", "distortion", "type", "label"):
                raw = item.get(key)
                if isinstance(raw, str) and raw.strip():
                    title = raw.strip()
                    break
            details = [
                raw.strip()
                for key in ("description", "explanation", "example")
                if isinstance(raw := item.get(key), str) and raw.strip()
            ]
            text = ": ".join([title, *details]) if title else ": ".join(details)
        else:
            raise ValueError("Элемент cognitive_distortions не является строкой")
        if text:
            result.append(text)
    return result


async def analyze_emotion(data: EmotionCreate) -> EmotionAnalysis:

    prompt = f"""
Ты — ИИ-помощник для ведения эмоционального дневника
на основе когнитивно-поведенческой терапии (КПТ).

Твоя задача:
1. Проанализировать ситуацию пользователя.
2. Найти возможные когнитивные искажения.
3. Предложить более сбалансированную альтернативную мысль.
4. Задать один вопрос для самостоятельного анализа.

Не ставь диагнозов.
Не утверждай, что твои интерпретации обязательно верны.

Данные пользователя:

Эмоция: {data.emotion_name}
Группа эмоций: {data.emotion_group}
Интенсивность: {data.intensity}
Ситуация: {data.situation}
Автоматическая мысль: {data.automatic_thought}

Верни только JSON-объект без Markdown.
Поле cognitive_distortions — массив строк.

{{
    "emotion_group": "{data.emotion_group}",
    "emotion_name": "{data.emotion_name}",
    "intensity": {data.intensity},
    "situation": "{data.situation}",
    "automatic_thought": "{data.automatic_thought}",
    "cognitive_distortions": [],
    "alternative_thought": "",
    "psychologist_question": ""
}}
"""

    response = await send_message(prompt)

    result = _extract_json(response)
    result["cognitive_distortions"] = _normalize_distortions(
        result.get("cognitive_distortions")
    )

    return EmotionAnalysis.model_validate(result)