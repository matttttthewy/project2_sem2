from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

class LanguageKeyboard:
    @staticmethod
    async def get_keyboard() -> ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🇷🇺 Русский")],
                [KeyboardButton(text="🇺🇸 English")],
                [KeyboardButton(text="🇪🇸 Español")],
                [KeyboardButton(text="🇩🇪 Deutsch")],
                [KeyboardButton(text="🇫🇷 Français")],
                [KeyboardButton(text="🇮🇹 Italiano")],
                [KeyboardButton(text="🇨🇳 中文")],
            ],
            resize_keyboard=True,
        )
        return keyboard 

LANGUAGE_MAPPING = {
    '🇺🇸 English': 'en',
    '🇷🇺 Русский': 'ru',
    '🇪🇸 Español': 'es',
    '🇩🇪 Deutsch': 'de',
    '🇫🇷 Français': 'fr',
    '🇮🇹 Italiano': 'it',
    '🇨🇳 中文': 'zh'
}