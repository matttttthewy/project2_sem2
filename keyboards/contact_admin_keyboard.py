from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class RoomsKeyboard:
    @staticmethod
    async def get_keyboard() -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Оставить заявку", callback_data="contact_admin")]
            ]
        )
        return keyboard