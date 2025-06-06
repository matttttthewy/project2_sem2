import os
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message, TelegramObject
from typing import Callable, Awaitable, Dict, Any
from services.translate_functions import translate_text
from services.translate_functions import get_user_language

# Middleware для перевода исходящих сообщений
class OutgoingTranslateMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Проверяем, что это исходящее сообщение
        if isinstance(event, Message) and hasattr(event, "text") and isinstance(event.text, str):
            user_id = event.chat.id  # для личных чатов
            user_lang = await get_user_language(user_id)
            translated = await translate_text(
                event.text,
                target_language=user_lang
            )
            event.text = translated
        return await handler(event, data)


