from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from config.bot_config import ADMIN_IDS, FAQ_STORAGE_PATH
from keyboards import AdminKeyboard, MainKeyboard, FAQModerateKeyboard, UserFaqKeyboard
from aiogram.types import Message, CallbackQuery
from storage import db
from storage.db_handler import DBHandler
import aiosqlite
from datetime import datetime, timedelta
from aiogram.fsm.state import State, StatesGroup
import asyncio
from utils import FaqDataHandler
from filters import NewUser, QuestionAlreadyExists
from services import PriceCalculator, GoogleSheetsManager
from states import FaqStates, StartStates, UserStates
from keyboards import LanguageKeyboard, LANGUAGE_MAPPING
from services import get_user_language, translate_text


general_router = Router(name="general_router")


@general_router.message(NewUser(db), CommandStart())
async def start_handler_new_user(message: Message, state: FSMContext):
    await state.set_state(StartStates.waiting_for_language)
    keyboard = await LanguageKeyboard.get_keyboard()
    await message.answer("Choose language:", reply_markup=keyboard)

# Обработчик команды /start
@general_router.message(CommandStart(), ~NewUser(db))
async def start_handler(message: Message, state: FSMContext, is_admin: bool = False):
    print("User id ", message.from_user.id)
    user = await db.get_user(telegram_id=str(message.from_user.id))
    keyboard = MainKeyboard.get_main_keyboard(user.language, is_admin)

    user_language = await get_user_language(db, message.from_user.id)
    welcome_text = await translate_text(MainKeyboard.welcome_message_ru, user_language)
            
    await message.answer(welcome_text, reply_markup=keyboard)

@general_router.message(StartStates.waiting_for_language)
async def process_language(message: Message, state: FSMContext):
    language = LANGUAGE_MAPPING[message.text]
    try:
        await db.create_user(
            telegram_nickname=message.from_user.username or "no_username",
            first_name=message.from_user.first_name,
            telegram_id=str(message.from_user.id),
            language=language,
            date_joined=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
    except Exception as e:
        await message.answer("Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.")
        return
    await state.clear()
    await start_handler(message, state)


@general_router.message(Command("settings"))
async def settings_handler(message: Message, state: FSMContext):
    await db.delete_user(telegram_id=str(message.from_user.id))
    await start_handler_new_user(message, state)


@general_router.message(Command("help"))
async def help_handler(message: Message, state: FSMContext):
    answer = "ℹ️ Список доступных команд: \n\n"
    answer += "🔹 /start – Начать работу с ботом \n"
    answer += "🔹 /faq – Часто задаваемые вопросы \n"
    answer += "🔹 /calculator – Калькулятор стоимости \n"
    answer += "🔹 /settings – Настройки бота \n"
    answer += "📌 Выберите нужную команду или воспользуйтесь кнопками меню."
    language = await get_user_language(db, message.from_user.id)
    answer = await translate_text(answer, language)
    await message.answer(answer)
    await state.clear()