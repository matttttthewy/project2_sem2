import json
from aiogram import Router, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from locales.button_locales import MainKeyboardLocales, AdminKeyboardLocales, FAQModerateKeyboardLocales

FILE_NAME = "buttons.json"

# Загрузка кнопок из json файла
def load_Buttons():
    try:
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"buttons": {}, "faq": {}}

# Сохранение кнопок в файл json
def save_Buttons(buttons):
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(buttons, f, ensure_ascii=False, indent=4)

# Загружаем кнопки при импорте модуля
reply_Buttons = load_Buttons()

# Состояния для разных операций с кнопками
class AddButtonStates(StatesGroup):
    waiting_for_button_text = State()
    waiting_for_reply = State()

class RemoveButtonStates(StatesGroup):
    waiting_for_button_text = State()

class EditButtonStates(StatesGroup):
    waiting_for_button_text = State()
    waiting_for_new_reply = State()

#Клавиатура для основных кнопок
class MainKeyboard:
    welcome_message_ru = (
        "👋 Добро пожаловать в бот отеля!\n\n"
        "🏨 Мы рады приветствовать вас в нашем уютном отеле, "
        "где каждый гость чувствует себя как дома.\n\n"
        "Через этого бота вы можете:\n"
        "✓ Узнать информацию об отеле\n"
        "✓ Посмотреть цены и доступные номера\n"
        "✓ Получить инструкции как до нас добраться\n"
        "✓ Связаться с администрацией\n"
        "✓ Получить ответы на часто задаваемые вопросы\n\n"
        "Выберите интересующий вас раздел в меню ниже 👇"
    )

    welcome_message_eng = (
        "👋 Welcome to the hotel bot!\n\n"
        "🏨 We are happy to welcome you to our cozy hotel, "
        "where every guest feels at home.\n\n"
        "Through this bot, you can:\n"
        "✓ Get information about the hotel\n"
        "✓ View prices and available rooms\n"
        "✓ Get instructions on how to get to us\n"
        "✓ Contact the administration\n"
        "✓ Get answers to frequently asked questions\n\n"
        "Select the section you are interested in below 👇"
    )

    @staticmethod
    def get_main_keyboard(language: str = "ru", is_admin: bool = False) -> ReplyKeyboardMarkup:
        
        keyboard = [
            [
                KeyboardButton(text=MainKeyboardLocales.texts[language if language in ['ru', 'en'] else 'en']["hotel"]),
                KeyboardButton(text=MainKeyboardLocales.texts[language if language in ['ru', 'en'] else 'en']["calculator"])
            ],
            [
                KeyboardButton(text=MainKeyboardLocales.texts[language if language in ['ru', 'en'] else 'en']["location"]),
                KeyboardButton(text=MainKeyboardLocales.texts[language if language in ['ru', 'en'] else 'en']["contact"])
            ],
            [
                KeyboardButton(text=MainKeyboardLocales.texts[language if language in ['ru', 'en'] else 'en']["faq"])
            ]
        ]
        if is_admin:
            keyboard.append([KeyboardButton(text=MainKeyboardLocales.texts[language if language in ['ru', 'en'] else 'en']["admin"])])

        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Клавиатура для админов
class AdminKeyboard:
    @staticmethod
    def get_admin_keyboard(language: str = "ru") -> ReplyKeyboardMarkup:
        
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=AdminKeyboardLocales.texts[language if language in ['ru', 'en'] else 'en']["stats"])],
                [KeyboardButton(text=AdminKeyboardLocales.texts[language if language in ['ru', 'en'] else 'en']["broadcast"])],
                [KeyboardButton(text=AdminKeyboardLocales.texts[language if language in ['ru', 'en'] else 'en']["rfaq"])],
                [KeyboardButton(text=AdminKeyboardLocales.texts[language if language in ['ru', 'en'] else 'en']["back"])]
            ],
            resize_keyboard=True
        )


class FAQModerateKeyboard:
    @staticmethod
    def get_faq_moderate_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
        
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=FAQModerateKeyboardLocales.menu_texts[language if language in ['ru', 'en'] else 'en']["add"], callback_data="add_faq")],
                [InlineKeyboardButton(text=FAQModerateKeyboardLocales.menu_texts[language if language in ['ru', 'en'] else 'en']["remove"], callback_data="remove_faq")],
                [InlineKeyboardButton(text=FAQModerateKeyboardLocales.menu_texts[language if language in ['ru', 'en'] else 'en']["edit"], callback_data="edit_faq")],
                [InlineKeyboardButton(text=FAQModerateKeyboardLocales.menu_texts[language if language in ['ru', 'en'] else 'en']["back"], callback_data="back_to_admin")]
            ]
        )

    @staticmethod
    def approve_delete_faq_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
        
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=FAQModerateKeyboardLocales.approve_delete_faq_texts[language if language in ['ru', 'en'] else 'en']["yes"], callback_data="approve_delete_faq")],
                [InlineKeyboardButton(text=FAQModerateKeyboardLocales.approve_delete_faq_texts[language if language in ['ru', 'en'] else 'en']["no"], callback_data="cancel_delete_faq")]
            ]
        )

    @staticmethod
    def chose_edit_action_faq_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
        
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=FAQModerateKeyboardLocales.edit_faq_texts[language if language in ['ru', 'en'] else 'en']["edit_question"], callback_data="edit_question_faq")],
                [InlineKeyboardButton(text=FAQModerateKeyboardLocales.edit_faq_texts[language if language in ['ru', 'en'] else 'en']["edit_answer"], callback_data="edit_answer_faq")],
                [InlineKeyboardButton(text=FAQModerateKeyboardLocales.edit_faq_texts[language if language in ['ru', 'en'] else 'en']["back"], callback_data="back_to_admin")]
            ]
        )