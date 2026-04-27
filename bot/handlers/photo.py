from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states import FoodAnalysis
from db import crud
from services import calc, nutrition, vision

router = Router()


@router.message(F.photo)
async def handle_photo(
    message: types.Message,
    bot: Bot,
    session: AsyncSession,
    state: FSMContext,
    i18n: I18nContext,
):
    user = await crud.get_user(session, message.from_user.id)
    if not user:
        return await message.answer("Please /start registration first.")

    status_msg = await message.answer(i18n.get("analyzing"))

    photo = message.photo[-1]
    photo_file = await bot.get_file(photo.file_id)
    photo_bytes = await bot.download_file(photo_file.file_path)

    vision_data = await vision.analyze_food_photo(photo_bytes.read())
    nutrition_data = await nutrition.get_nutrition_data(
        vision_data["dish_name"], vision_data["weight_g"]
    )

    if not nutrition_data:
        return await status_msg.edit_text(i18n.get("not-found"))

    await state.update_data(
        dish_name=vision_data["dish_name"],
        weight_g=vision_data["weight_g"],
        carbs=nutrition_data["carbs"],
        protein=nutrition_data["protein"],
        fat=nutrition_data["fat"],
        kcal=nutrition_data["kcal"],
        photo_id=photo.file_id,
    )

    await state.set_state(FoodAnalysis.waiting_for_bg)
    await status_msg.edit_text(
        i18n.get(
            "ask-bg",
            dish=vision_data["dish_name"],
            weight=vision_data["weight_g"],
            carbs=round(nutrition_data["carbs"], 1),
        )
    )


@router.message(FoodAnalysis.waiting_for_bg)
async def process_bg(
    message: types.Message, session: AsyncSession, state: FSMContext, i18n: I18nContext
):
    user = await crud.get_user(session, message.from_user.id)
    data = await state.get_data()

    current_bg = None
    if message.text != "/skip":
        try:
            current_bg = float(message.text.replace(",", "."))
        except ValueError:
            return await message.answer(i18n.get("error-number"))

    bolus = calc.calculate_bolus(
        carbs=data["carbs"],
        icr=user.icr,
        isf=user.isf,
        target_bg=user.target_bg,
        current_bg=current_bg,
    )

    await crud.create_meal_log(
        session=session,
        user_id=user.id,
        dish_name=data["dish_name"],
        portion_g=data["weight_g"],
        carbs_g=data["carbs"],
        kcal=data["kcal"],
        protein_g=data["protein"],
        fat_g=data["fat"],
        bolus_dose=bolus["total_dose"],
        current_bg=current_bg,
        photo_file_id=data["photo_id"],
    )

    await state.clear()
    await message.answer(
        i18n.get(
            "result-bolus",
            total=bolus["total_dose"],
            type=user.insulin_type,
            carb_dose=bolus["carb_dose"],
            correction=bolus["correction_dose"],
            dish=data["dish_name"],
            carbs=round(data["carbs"], 1),
            kcal=int(data["kcal"]),
        )
    )
