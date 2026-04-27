from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards import main_menu
from bot.states import Registration
from core.i18n import I18n
from db import crud

router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: types.Message, session: AsyncSession, state: FSMContext, i18n: I18n
):
    user = await crud.get_user(session, message.from_user.id)
    if user:
        return await message.answer(
            i18n.get("already-reg"), reply_markup=main_menu(i18n)
        )

    await state.set_state(Registration.waiting_for_icr)
    await message.answer(i18n.get("start-welcome"))


@router.message(Registration.waiting_for_icr, F.text)
async def process_icr(message: types.Message, state: FSMContext, i18n: I18n):
    try:
        icr = float(message.text.replace(",", "."))
        await state.update_data(icr=icr)
        await state.set_state(Registration.waiting_for_isf)
        await message.answer(i18n.get("enter-isf"))
    except ValueError:
        await message.answer(i18n.get("error-number"))


@router.message(Registration.waiting_for_isf, F.text)
async def process_isf(message: types.Message, state: FSMContext, i18n: I18n):
    try:
        isf = float(message.text.replace(",", "."))
        await state.update_data(isf=isf)
        await state.set_state(Registration.waiting_for_target_bg)
        await message.answer(i18n.get("enter-target"))
    except ValueError:
        await message.answer(i18n.get("error-number"))


@router.message(Registration.waiting_for_target_bg, F.text)
async def process_target_bg(message: types.Message, state: FSMContext, i18n: I18n):
    try:
        target_bg = float(message.text.replace(",", "."))
        await state.update_data(target_bg=target_bg)
        await state.set_state(Registration.waiting_for_insulin_type)
        await message.answer(i18n.get("enter-insulin"))
    except ValueError:
        await message.answer(i18n.get("error-number"))


@router.message(Registration.waiting_for_insulin_type, F.text)
async def process_insulin_type(
    message: types.Message, session: AsyncSession, state: FSMContext, i18n: I18n
):
    data = await state.get_data()
    await crud.create_user(
        session=session,
        id=message.from_user.id,
        username=message.from_user.username,
        icr=data["icr"],
        isf=data["isf"],
        target_bg=data["target_bg"],
        insulin_type=message.text,
        language=i18n.lang,
    )
    await state.clear()
    await message.answer(i18n.get("reg-complete"), reply_markup=main_menu(i18n))
