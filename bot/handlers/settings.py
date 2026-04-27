from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards import language_menu, main_menu
from bot.states import Settings as SettingsState
from core.i18n import I18n
from db import crud

router = Router()


@router.message(Command("settings"))
@router.message(F.text.in_({"⚙️ Settings", "⚙️ Налаштування"}))
async def cmd_settings(
    message: types.Message, session: AsyncSession, state: FSMContext, i18n: I18n
):
    await state.clear()
    user = await crud.get_user(session, message.from_user.id)

    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text=i18n.get("btn-edit-icr"), callback_data="edit:icr"
        ),
        types.InlineKeyboardButton(
            text=i18n.get("btn-edit-isf"), callback_data="edit:isf"
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text=i18n.get("btn-edit-target_bg"), callback_data="edit:target_bg"
        ),
        types.InlineKeyboardButton(
            text=i18n.get("btn-edit-insulin_type"), callback_data="edit:insulin_type"
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text=i18n.get("btn-change-lang"), callback_data="change_lang"
        )
    )

    await message.answer(
        i18n.get(
            "settings-main",
            lang="English" if user.language == "en" else "Українська",
            icr=user.icr,
            isf=user.isf,
            target=user.target_bg,
            type=user.insulin_type,
        ),
        reply_markup=builder.as_markup(),
    )


@router.callback_query(F.data.startswith("edit:"))
async def process_edit_field(
    callback: types.CallbackQuery, state: FSMContext, i18n: I18n
):
    field = callback.data.split(":")[1]
    await state.set_state(SettingsState.waiting_for_value)
    await state.update_data(edit_field=field)

    prompt_key = f"prompt-edit-{field}"
    await callback.message.answer(i18n.get(prompt_key))
    await callback.answer()


@router.message(SettingsState.waiting_for_value, F.text)
async def process_new_value(
    message: types.Message, session: AsyncSession, state: FSMContext, i18n: I18n
):
    data = await state.get_data()
    field = data.get("edit_field")

    value = message.text
    if field in ["icr", "isf", "target_bg"]:
        try:
            value = float(value.replace(",", "."))
        except ValueError:
            return await message.answer(i18n.get("error-number"))

    await crud.update_user(session, message.from_user.id, **{field: value})
    await state.clear()

    await message.answer(i18n.get("profile-updated"))
    await cmd_settings(message, session, state, i18n)


@router.callback_query(F.data == "change_lang")
async def process_change_lang(
    callback: types.CallbackQuery, session: AsyncSession, i18n: I18n
):
    user = await crud.get_user(session, callback.from_user.id)
    await callback.message.edit_text(
        i18n.get("select-lang"), reply_markup=language_menu(user.language)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_lang:"))
async def process_set_lang(
    callback: types.CallbackQuery, session: AsyncSession, i18n: I18n
):
    new_lang = callback.data.split(":")[1]
    user = await crud.get_user(session, callback.from_user.id)

    if user.language != new_lang:
        await crud.update_user_language(session, user.id, new_lang)
        i18n.lang = new_lang

        # Update Reply Keyboard as well by sending a confirmation message
        await callback.message.answer(
            i18n.get("lang-changed"), reply_markup=main_menu(i18n)
        )

    # Go back to settings or just delete selection menu
    await callback.message.delete()
    await callback.answer()
