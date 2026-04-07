from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from handlers.keyboards import get_start_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Выберите действие:",
        reply_markup=get_start_keyboard()
    )
