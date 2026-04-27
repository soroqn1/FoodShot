from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards import weight_adjust_keyboard
from bot.states import FoodAnalysis
from core.i18n import I18n
from db import crud
from services import calc, nutrition, vision

router = Router()


def _ask_bg_text(i18n: I18n, data: dict) -> str:
    return i18n.get(
        "ask-bg",
        dish=data["dish_name"],
        weight=data["weight_g"],
        carbs=round(data["carbs_per_g"] * data["weight_g"], 1),
        kcal=int(data["kcal_per_g"] * data["weight_g"]),
        confidence=i18n.get(f"confidence-{data['confidence']}"),
    )


@router.message(F.photo)
async def handle_photo(
    message: types.Message,
    bot: Bot,
    session: AsyncSession,
    state: FSMContext,
    i18n: I18n,
):
    user = await crud.get_user(session, message.from_user.id)
    if not user:
        return await message.answer("Please /start registration first.")

    status_msg = await message.answer(i18n.get("analyzing"))

    photo = message.photo[-1]
    photo_file = await bot.get_file(photo.file_id)
    photo_bytes = await bot.download_file(photo_file.file_path)

    vision_data = await vision.analyze_food_photo(
        photo_bytes.read(), language=user.language
    )
    if not vision_data:
        return await status_msg.edit_text(i18n.get("not-found"))

    dish_display = vision_data["dish_name"]
    dish_en = vision_data.get("dish_name_en", dish_display)
    weight_g = vision_data["weight_g"]
    confidence = vision_data.get("confidence", "medium")

    nutrition_data = await nutrition.get_nutrition_data(dish_en, weight_g)
    if not nutrition_data:
        return await status_msg.edit_text(i18n.get("not-found"))

    state_data = {
        "dish_name": dish_display,
        "dish_en": dish_en,
        "weight_g": weight_g,
        "carbs_per_g": nutrition_data["carbs"] / weight_g,
        "protein_per_g": nutrition_data["protein"] / weight_g,
        "fat_per_g": nutrition_data["fat"] / weight_g,
        "kcal_per_g": nutrition_data["kcal"] / weight_g,
        "confidence": confidence,
        "photo_id": photo.file_id,
    }
    await state.update_data(**state_data)
    await state.set_state(FoodAnalysis.waiting_for_bg)

    await status_msg.edit_text(
        _ask_bg_text(i18n, state_data),
        reply_markup=weight_adjust_keyboard(weight_g),
    )


@router.callback_query(FoodAnalysis.waiting_for_bg, F.data.startswith("weight:"))
async def process_weight_adjust(
    callback: types.CallbackQuery, state: FSMContext, i18n: I18n
):
    delta = int(callback.data.split(":")[1])
    data = await state.get_data()

    new_weight = max(10, data["weight_g"] + delta)
    await state.update_data(weight_g=new_weight)
    data["weight_g"] = new_weight

    await callback.message.edit_text(
        _ask_bg_text(i18n, data),
        reply_markup=weight_adjust_keyboard(new_weight),
    )
    await callback.answer()


@router.message(FoodAnalysis.waiting_for_bg, F.text)
async def process_bg(
    message: types.Message, session: AsyncSession, state: FSMContext, i18n: I18n
):
    if message.text and message.text.startswith("/"):
        await state.clear()
        return

    user = await crud.get_user(session, message.from_user.id)
    data = await state.get_data()

    current_bg = None
    if message.text != "/skip":
        try:
            current_bg = float(message.text.replace(",", "."))
        except ValueError:
            return await message.answer(i18n.get("error-number"))

    weight_g = data["weight_g"]
    carbs = data["carbs_per_g"] * weight_g
    kcal = int(data["kcal_per_g"] * weight_g)

    bolus = calc.calculate_bolus(
        carbs=carbs,
        icr=user.icr,
        isf=user.isf,
        target_bg=user.target_bg,
        current_bg=current_bg,
    )

    await crud.create_meal_log(
        session=session,
        user_id=user.id,
        dish_name=data["dish_name"],
        portion_g=weight_g,
        carbs_g=carbs,
        kcal=kcal,
        protein_g=data["protein_per_g"] * weight_g,
        fat_g=data["fat_per_g"] * weight_g,
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
            carbs=round(carbs, 1),
            kcal=kcal,
            icr=user.icr,
            isf=user.isf,
            target=user.target_bg,
        )
    )
