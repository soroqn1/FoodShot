from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_for_icr = State()
    waiting_for_isf = State()
    waiting_for_target_bg = State()
    waiting_for_insulin_type = State()


class FoodAnalysis(StatesGroup):
    waiting_for_confirmation = State()
    waiting_for_bg = State()


class Settings(StatesGroup):
    waiting_for_value = State()
