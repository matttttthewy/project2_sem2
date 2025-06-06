import os
import aiohttp
from aiohttp import ClientError
from dotenv import load_dotenv
import aiosqlite
import asyncio

from typing import Dict, Tuple

load_dotenv()
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")

# Простой in-memory кеш
_translation_cache: Dict[Tuple[str, str, str], str] = {}

async def translate_text(text: str, target_language: str = "en", source_language: str = "ru") -> str:
    if target_language == source_language:
        return text

    # Проверка кеша
    cache_key = (text, source_language, target_language)
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]

    url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "sourceLanguageCode": source_language,
        "targetLanguageCode": target_language,
        "texts": [text]
    }

    try:
        timeout = aiohttp.ClientTimeout(total=5)  # таймаут на весь запрос
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=body, headers=headers) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"[ERROR] Translation API responded with {resp.status}: {error_text}")
                    return text  # Возвращаем оригинал в случае ошибки

                data = await resp.json()
                translated = data["translations"][0]["text"]

                # Сохраняем в кеш
                _translation_cache[cache_key] = translated
                return translated

    except asyncio.TimeoutError:
        print("[ERROR] Translation request timed out")
    except ClientError as e:
        print(f"[ERROR] HTTP error during translation: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error during translation: {e}")

    return text  # fallback — возвращаем оригинал при ошибках


async def get_user_language(db, telegram_id: int) -> str:
    user = await db.get_user(telegram_id=str(telegram_id))
    if user and getattr(user, "language", None):
        return user.language[:2]
    return "ru"  # язык по умолчанию