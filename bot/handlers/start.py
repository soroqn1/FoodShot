from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states import Registration
from core.locales import get_text
from db import crud

router = Router()


def get_user_lang(message: types.Message) -> str:
    lang = message.from_user.language_code
    return lang if lang in ["uk", "en"] else "en"


@router.message(CommandStart())
async def cmd_start(message: types.Message, session: AsyncSession, state: FSMContext):
    user = await crud.get_user(session, message.from_user.id)
    lang = user.language if user else get_user_lang(message)

    if user:
        return await message.answer(get_text("already_reg", lang))

    await state.update_data(lang=lang)
    await state.set_state(Registration.waiting_for_icr)
    await message.answer(get_text("start_welcome", lang))


@router.message(Registration.waiting_for_icr, F.text)
async def process_icr(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    try:
        icr = float(message.text.replace(",", "."))
        await state.update_data(icr=icr)
        await state.set_state(Registration.waiting_for_isf)
        await message.answer(get_text("enter_isf", lang))
    except ValueError:
        await message.answer(get_text("error_number", lang))


@router.message(Registration.waiting_for_isf, F.text)
async def process_isf(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    try:
        isf = float(message.text.replace(",", "."))
        await state.update_data(isf=isf)
        await state.set_state(Registration.waiting_for_target_bg)
        await message.answer(get_text("enter_target", lang))
    except ValueError:
        await message.answer(get_text("error_number", lang))


@router.message(Registration.waiting_for_target_bg, F.text)
async def process_target_bg(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    try:
        target_bg = float(message.text.replace(",", "."))
        await state.update_data(target_bg=target_bg)
        await state.set_state(Registration.waiting_for_insulin_type)
        await message.answer(get_text("enter_insulin", lang))
    except ValueError:
        await message.answer(get_text("error_number", lang))


@router.message(Registration.waiting_for_insulin_type, F.text)
async def process_insulin_type(
    message: types.Message, session: AsyncSession, state: FSMContext
):
    data = await state.get_data()
    lang = data.get("lang", "en")
    await crud.create_user(
        session=session,
        id=message.from_user.id,
        username=message.from_user.username,
        icr=data["icr"],
        isf=data["isf"],
        target_bg=data["target_bg"],
        insulin_type=message.text,
        language=lang,
    )
    await state.clear()
    await message.answer(get_text("reg_complete", lang))
