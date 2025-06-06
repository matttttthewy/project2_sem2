from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config.bot_config import ADMIN_IDS, FAQ_STORAGE_PATH, GOOGLE_CREDENTIALS_PATH, SPREADSHEET_ID
from keyboards import AdminKeyboard, MainKeyboard, FAQModerateKeyboard, UserFaqKeyboard
from aiogram.types import Message, CallbackQuery
from storage import db
import aiosqlite
from datetime import datetime, timedelta
from aiogram.fsm.state import State, StatesGroup
import asyncio
from utils import FaqDataHandler
from filters import QuestionAlreadyExists
from services import PriceCalculator, GoogleSheetsManager
from states import FaqStates, UserStates
from locales.button_locales import MainKeyboardLocales
from services import translate_text, get_user_language
from handlers.general_hanlders import start_handler


user_router = Router(name="user_router")
price_calculator = PriceCalculator(GoogleSheetsManager(
    creds_path=GOOGLE_CREDENTIALS_PATH,
    spreadsheet_id=SPREADSHEET_ID
))


@user_router.message(lambda message: message.text in [MainKeyboardLocales.texts.get(language, "en")["faq"] for language in ["ru", "en"]] or message.text == "/faq")
async def faq_handler(message: Message, state: FSMContext):
    questions = FaqDataHandler.get_questions(FAQ_STORAGE_PATH)
    keyboard = await UserFaqKeyboard.get_keyboard(questions)
    answer = "Выберите вопрос:"
    language = await get_user_language(db, message.from_user.id)
    answer = await translate_text(answer, language)
    await message.answer(answer, reply_markup=keyboard)
    await state.set_state(FaqStates.waiting_for_question)

@user_router.message(FaqStates.waiting_for_question)
async def process_question(message: Message, state: FSMContext, is_admin: bool = False):
    question = message.text
    answer = FaqDataHandler.get_answer(FAQ_STORAGE_PATH, question)
    if not answer:
        await state.clear()
        await start_handler(message, state, is_admin)
        return
    await message.answer(answer, reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


@user_router.message(lambda message: message.text == "💰 Калькулятор стоимости" or message.text == "💰 Price calculator" or message.text == "/calculator")
async def process_start_date(message: Message, state: FSMContext):
    await state.set_state(UserStates.waiting_for_start_date)
    answer = "Пожалуйста, укажите дату заезда в формате ДД.ММ"
    language = await get_user_language(db, message.from_user.id)
    answer = await translate_text(answer, language)
    await message.answer(answer, reply_markup=types.ReplyKeyboardRemove())


@user_router.message(UserStates.waiting_for_start_date)
async def process_end_date(message: Message, state: FSMContext):
    await state.set_state(UserStates.waiting_for_end_date)
    await state.update_data(start_date=message.text)
    answer = "Пожалуйста, укажите дату выезда в формате ДД.ММ"
    language = await get_user_language(db, message.from_user.id)
    answer = await translate_text(answer, language)
    await message.answer(answer)


@user_router.message(UserStates.waiting_for_end_date)
async def process_adults(message: Message, state: FSMContext):
    await state.set_state(UserStates.waiting_for_adults)
    await state.update_data(end_date=message.text)
    answer = "Сколько взрослых будет проживать?"
    language = await get_user_language(db, message.from_user.id)
    answer = await translate_text(answer, language)
    await message.answer(answer)


@user_router.message(UserStates.waiting_for_adults)
async def process_children(message: Message, state: FSMContext):
    await state.set_state(UserStates.waiting_for_children)
    await state.update_data(adults=message.text)
    answer = "Сколько детей будет проживать?"
    language = await get_user_language(db, message.from_user.id)
    answer = await translate_text(answer, language)
    await message.answer(answer)


@user_router.message(UserStates.waiting_for_children)
async def calculate_price(message: Message, state: FSMContext):
    data = await state.get_data()
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    adults = data.get("adults")
    children = message.text

    if datetime.strptime(end_date, "%d.%m") < datetime.strptime(start_date, "%d.%m"):
        language = await get_user_language(db, message.from_user.id)
        error_msg = "Bombardiro Crocodilo?"
        error_msg = await translate_text(error_msg, language)
        await message.answer(error_msg)
        await state.clear()
        return

    try:
        price_message = await price_calculator.calculate_best_price(start_date, end_date, int(adults), int(children))
        answer = price_message.message
    except Exception as e:
        print(e)
        answer = "Упс, что-то пошло не так. Пожалуйста, проверьте правильность введенных данных и попробуйте позже."
    language = await get_user_language(db, message.from_user.id)
    answer = await translate_text(answer, language)
    await message.answer(answer)
    await state.clear()
    if price_message.status == PriceCalculator.TOO_MANY_GUESTS:
        await state.set_state(UserStates.waiting_for_room_scheme)

@user_router.message(lambda message: message.text == "🏨 О нашем отеле" or message.text == "🏨 About our hotel")
async def about_hotel_handler(message: Message, state: FSMContext):
    text = "Отель Гранат в Лермонтово — идеальное место для отдыха у моря! 5 минут до пляжа, уютные номера, трехразовое питание включено, подогреваемые бассейны с горками и джакузи, анимация, бар, мангальная зона и развлечения для всей семьи. Парковка, шезлонги, цветущий двор и комфорт — всё для вашего отдыха!"
    language = await get_user_language(db, message.from_user.id)
    text = await translate_text(text, language)
    await message.answer(text)
    await state.clear()


@user_router.message(lambda message: message.text == "📍 Как добраться" or message.text == "📍 How to get there")
async def how_to_get_there_handler(message: Message, state: FSMContext):
    language = await get_user_language(db, message.from_user.id)
    text = "🚉 Ближайший железнодорожный вокзал — г. Туапсе.Все поезда, следующие до Адлера, делают остановку в Туапсе.\n\n"
    text += "🚗 От Туапсе до Лермонтово — около 45 км (примерно 1 час в пути).Мы можем организовать трансфер, но чаще всего выгоднее заказать такси через Яндекс.Такси — это быстрее и по оптимальной цене.\n\n"
    text += "Если вам нужна помощь с маршрутом — всегда подскажем!"

    text = await translate_text(text, language)
    await message.answer(text)
    await state.clear()


@user_router.message(lambda message: message.text == "📞 Связаться с нами" or message.text == "📞 Contact us")
async def contact_us_handler(message: Message, state: FSMContext):
    text = "📞 По всем вопросам можно написать нам:@Granat_Admin\n\nИли перейти на сайт: https://granat-lermontovo.ru"
    language = await get_user_language(db, message.from_user.id)
    text = await translate_text(text, language)
    await message.answer(text)
    await state.clear()



