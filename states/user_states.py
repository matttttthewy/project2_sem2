from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    waiting_for_language = State()
    waiting_for_question = State()
    waiting_for_start_date = State()
    waiting_for_end_date = State()
    waiting_for_adults = State()
    waiting_for_children = State()
    waiting_for_room_scheme = State()