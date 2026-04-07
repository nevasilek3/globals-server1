from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import SessionLocal
from database.models import User, Subscription, ApiKey
from handlers.keyboards import get_start_keyboard, get_profile_keyboard, get_subscription_keyboard
from config import SUBSCRIPTION_PLANS
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import secrets

router = Router()


class ProfileStates(StatesGroup):
    waiting_for_api_key = State()


# Хранилище активных сессий (импортируем из auth.py)
user_sessions = {}


def get_user_from_session(user_id: int) -> User:
    """Получить пользователя из сессии"""
    return user_sessions.get(user_id)


def show_profile(user: User) -> str:
    """Форматирует информацию профиля"""
    sub_end = user.subscription_end.strftime("%d.%m.%Y") if user.subscription_end else "Нет подписки"
    
    return (
        f"👤 <b>Профиль</b>\n"
        f"🆔 UID: <code>{user.id}</code>\n"
        f"📧 Email: <code>{user.email}</code>\n"
        f"👤 Username: <code>{user.username}</code>\n"
        f"💻 VDS: {user.pc_type or 'Не установлен'}\n"
        f"📅 Подписка до: {sub_end}"
    )


@router.message(F.text == "💳 Купить/Продлить подписку")
async def buy_subscription(message: Message):
    """Показывает варианты подписки"""
    user = get_user_from_session(message.from_user.id)
    
    if not user:
        await message.answer("❌ Вы не авторизованы", reply_markup=get_start_keyboard())
        return
    
    await message.answer(
        "💳 Выберите тариф подписки:",
        reply_markup=get_subscription_keyboard()
    )


@router.callback_query(F.data.startswith("sub_"))
async def process_subscription(callback: CallbackQuery):
    """Обработка выбора подписки"""
    user = get_user_from_session(callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Вы не авторизованы", show_alert=True)
        return
    
    plan = callback.data.replace("sub_", "")
    
    if plan not in SUBSCRIPTION_PLANS:
        await callback.answer("❌ Неизвестный тариф", show_alert=True)
        return
    
    db = SessionLocal()
    try:
        # Обновляем дату подписки
        days = SUBSCRIPTION_PLANS[plan]["days"]
        new_end_date = datetime.utcnow() + timedelta(days=days)
        
        user.subscription_end = new_end_date
        db.commit()
        
        # Обновляем в сессии
        user_sessions[callback.from_user.id] = user
        
        await callback.answer(f"✅ Подписка активирована на {days} дней!", show_alert=True)
        await callback.message.edit_text(
            f"✅ Подписка активирована!\n\n"
            f"📅 Действительна до: {new_end_date.strftime('%d.%m.%Y')}"
        )
    finally:
        db.close()


@router.callback_query(F.data == "cancel_sub")
async def cancel_subscription(callback: CallbackQuery):
    """Отмена выбора подписки"""
    await callback.message.delete()
    await callback.answer()


@router.message(F.text == "🔑 Ввести ключ")
async def enter_api_key(message: Message, state: FSMContext):
    """Начало ввода API ключа"""
    user = get_user_from_session(message.from_user.id)
    
    if not user:
        await message.answer("❌ Вы не авторизованы", reply_markup=get_start_keyboard())
        return
    
    await state.set_state(ProfileStates.waiting_for_api_key)
    await message.answer("🔑 Введите ключ подписки:")


@router.message(ProfileStates.waiting_for_api_key)
async def process_api_key(message: Message, state: FSMContext):
    """Обработка введенного ключа"""
    user = get_user_from_session(message.from_user.id)
    api_key = message.text.strip()
    
    db = SessionLocal()
    try:
        # Проверяем ключ
        key_record = db.query(ApiKey).filter(
            ApiKey.key == api_key,
            ApiKey.is_active == True
        ).first()
        
        if not key_record:
            await message.answer("❌ Ключ не найден или уже использован")
        elif key_record.expires_at and key_record.expires_at < datetime.utcnow():
            await message.answer("❌ Ключ истек")
        else:
            # Активируем ключ
            key_record.is_active = False
            
            # Добавляем дни подписки
            days = 30  # По умолчанию 30 дней
            if user.subscription_end and user.subscription_end > datetime.utcnow():
                new_end = user.subscription_end + timedelta(days=days)
            else:
                new_end = datetime.utcnow() + timedelta(days=days)
            
            user.subscription_end = new_end
            db.commit()
            
            # Обновляем в сессии
            user_sessions[message.from_user.id] = user
            
            await message.answer(
                f"✅ Ключ активирован!\n"
                f"📅 Подписка продлена до: {new_end.strftime('%d.%m.%Y')}"
            )
    finally:
        db.close()
    
    await state.clear()


@router.message(F.text == "🔄 Сбросить VDS")
async def reset_vds(message: Message):
    """Сброс типа VDS"""
    user = get_user_from_session(message.from_user.id)
    
    if not user:
        await message.answer("❌ Вы не авторизованы", reply_markup=get_start_keyboard())
        return
    
    db = SessionLocal()
    try:
        user.pc_type = None
        db.commit()
        user_sessions[message.from_user.id] = user
        
        await message.answer("✅ VDS сброшен", reply_markup=get_profile_keyboard())
    finally:
        db.close()


@router.message(F.text == "🚪 Выйти")
async def logout(message: Message):
    """Выход из аккаунта"""
    if message.from_user.id in user_sessions:
        del user_sessions[message.from_user.id]
    
    await message.answer(
        "👋 Вы вышли из аккаунта",
        reply_markup=get_start_keyboard()
    )
