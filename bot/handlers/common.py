from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from core.i18n import I18n

router = Router()


@router.message(Command("help"))
async def cmd_help(message: types.Message, state: FSMContext, i18n: I18n):
    await state.clear()
    await message.answer(i18n.get("menu-main"))
