from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я FoodShot. Пока что я работаю в режиме эхо-бота.")


@router.message()
async def echo_handler(message: types.Message):
    try:
        await message.send_copy(chat_id=message.chat.id)
    except Exception:
        await message.answer(message.text)
