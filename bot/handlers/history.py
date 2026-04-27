from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from core.i18n import I18n
from db import crud

router = Router()


@router.message(Command("history"))
@router.message(F.text.in_({"📜 History", "📜 Історія"}))
async def cmd_history(
    message: types.Message, session: AsyncSession, state: FSMContext, i18n: I18n
):
    await state.clear()
    meals = await crud.get_user_history(session, message.from_user.id, limit=10)

    if not meals:
        return await message.answer(i18n.get("history-empty"))

    text = i18n.get("history-header") + "\n"

    for meal in meals:
        date_str = meal.created_at.strftime("%d.%m %H:%M")
        text += (
            i18n.get(
                "history-item",
                date=date_str,
                dish=meal.dish_name,
                carbs=round(meal.carbs_g, 1),
                bolus=meal.bolus_dose,
            )
            + "\n\n"
        )

    await message.answer(text)
