
# NOTE: Данный код не используется, и его можно смело удалять :)


from aiogram import Router, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config.bot_config import ADMIN_IDS
from keyboards.keyboards import AddButtonStates, RemoveButtonStates, EditButtonStates, reply_Buttons, save_Buttons, load_Buttons, FILE_NAME


keyboard_router = Router(name="keyboard_router")


# Обработчик /menu
@keyboard_router.message(Command("menu"))
async def show_menu(message: types.Message):
    # Создаем список кнопок
    buttons = [[KeyboardButton(text=text)] for text in reply_Buttons.keys()]
    
    # Создаем клавиатуру с кнопками
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer("Меню кнопок:", reply_markup=keyboard)

# Команда /add_button 
@keyboard_router.message(Command("add_button"))
async def add_button(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_IDSS:
        await message.answer("У вас нет прав.")
        return
    await message.answer("Введите текст новой кнопки:")
    await state.set_state(AddButtonStates.waiting_for_button_text)

@keyboard_router.message(AddButtonStates.waiting_for_button_text)
async def get_new_button_text(message: types.Message, state: FSMContext):
    button_text = message.text
    if button_text in reply_Buttons:
        await message.answer("Кнопка уже существует. Введите другой текст.")
        return
    await state.update_data(button_text=button_text)
    await message.answer("Введите ответ для этой кнопки:")
    await state.set_state(AddButtonStates.waiting_for_reply)

@keyboard_router.message(AddButtonStates.waiting_for_reply)
async def get_new_button_reply(message: types.Message, state: FSMContext):
    reply_text = message.text
    data = await state.get_data()
    button_text = data.get('button_text')
    reply_Buttons[button_text] = reply_text
    save_Buttons(reply_Buttons)
    await message.answer(f"Кнопка '{button_text}' добавлена с ответом:\n{reply_text}")
    await state.clear()

# Команда /remove_button
@keyboard_router.message(Command("remove_button"))
async def remove_button(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_IDSS:
        await message.answer("У вас нет прав.")
        return
    if not reply_Buttons:
        await message.answer("Список кнопок пуст.")
        return
    await message.answer("Введите текст кнопки для удаления:\n" + "\n".join(reply_Buttons.keys()))
    await state.set_state(RemoveButtonStates.waiting_for_button_text)

@keyboard_router.message(RemoveButtonStates.waiting_for_button_text)
async def remove_button_text(message: types.Message, state: FSMContext):
    button_text = message.text
    if button_text in reply_Buttons:
        del reply_Buttons[button_text]
        save_Buttons(reply_Buttons)
        await message.answer(f"Кнопка '{button_text}' удалена.")
    else:
        await message.answer("Такой кнопки нет.")
    await state.clear()

# Команда /list_buttons
@keyboard_router.message(Command("list_buttons"))
async def list_buttons(message: types.Message):
    if not reply_Buttons:
        await message.answer("Список кнопок пуст.")
        return
    response = "Список кнопок и их ответов:\n\n"
    for btn, reply in reply_Buttons.items():
        response += f"🔘 {btn}: {reply}\n"
    await message.answer(response)

# Команда /edit_button
@keyboard_router.message(Command("edit_button"))
async def edit_button(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_IDSS:
        await message.answer("У вас нет прав.")
        return
    if not reply_Buttons:
        await message.answer("Список кнопок пуст.")
        return
    await message.answer("Введите текст кнопки для редактирования:\n" + "\n".join(reply_Buttons.keys()))
    await state.set_state(EditButtonStates.waiting_for_button_text)

@keyboard_router.message(EditButtonStates.waiting_for_button_text)
async def get_button_to_edit(message: types.Message, state: FSMContext):
    button_text = message.text
    if button_text not in reply_Buttons:
        await message.answer("Такой кнопки нет.")
        await state.clear()
        return
    await state.update_data(button_text=button_text)
    await message.answer(f"Введите новый ответ для кнопки '{button_text}':")
    await state.set_state(EditButtonStates.waiting_for_new_reply)

@keyboard_router.message(EditButtonStates.waiting_for_new_reply)
async def get_new_reply_text(message: types.Message, state: FSMContext):
    new_reply = message.text
    data = await state.get_data()
    button_text = data.get('button_text')
    reply_Buttons[button_text] = new_reply
    save_Buttons(reply_Buttons)
    await message.answer(f"Ответ для кнопки '{button_text}' обновлён:\n{new_reply}")
    await state.clear()

