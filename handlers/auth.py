from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import SessionLocal
from utils.auth import login_user, register_user
from handlers.keyboards import get_start_keyboard, get_profile_keyboard
from datetime import datetime

router = Router()


class AuthStates(StatesGroup):
    waiting_for_login_username = State()
    waiting_for_login_password = State()
    waiting_for_register_email = State()
    waiting_for_register_username = State()
    waiting_for_register_password = State()


# Хранилище активных сессий пользователей
user_sessions = {}


@router.message(F.text == "🔐 Авторизация")
async def start_login(message: Message, state: FSMContext):
    """Начало авторизации"""
    await state.set_state(AuthStates.waiting_for_login_username)
    await message.answer("📝 Введите ваш username:")


@router.message(AuthStates.waiting_for_login_username)
async def get_login_username(message: Message, state: FSMContext):
    """Получение username для авторизации"""
    await state.update_data(username=message.text)
    await state.set_state(AuthStates.waiting_for_login_password)
    await message.answer("🔑 Введите ваш пароль:")


@router.message(AuthStates.waiting_for_login_password)
async def get_login_password(message: Message, state: FSMContext):
    """Получение пароля и авторизация"""
    data = await state.get_data()
    username = data.get("username")
    password = message.text
    
    db = SessionLocal()
    try:
        success, user, msg = login_user(db, username, password)
        
        if success:
            # Сохраняем сессию
            user_sessions[message.from_user.id] = user
            
            # Формируем информацию профиля
            sub_end = user.subscription_end.strftime("%d.%m.%Y") if user.subscription_end else "Нет подписки"
            
            profile_text = (
                f"✅ {msg}\n\n"
                f"👤 <b>Профиль</b>\n"
                f"🆔 UID: <code>{user.id}</code>\n"
                f"📧 Email: <code>{user.email}</code>\n"
                f"👤 Username: <code>{user.username}</code>\n"
                f"💻 VDS: {user.pc_type or 'Не установлен'}\n"
                f"📅 Подписка до: {sub_end}"
            )
            
            await message.answer(profile_text, parse_mode="HTML", reply_markup=get_profile_keyboard())
        else:
            await message.answer(msg, reply_markup=get_start_keyboard())
    finally:
        db.close()
    
    await state.clear()


@router.message(F.text == "📝 Регистрация")
async def start_register(message: Message, state: FSMContext):
    """Начало регистрации"""
    await state.set_state(AuthStates.waiting_for_register_email)
    await message.answer("📧 Введите ваш email:")


@router.message(AuthStates.waiting_for_register_email)
async def get_register_email(message: Message, state: FSMContext):
    """Получение email для регистрации"""
    await state.update_data(email=message.text)
    await state.set_state(AuthStates.waiting_for_register_username)
    await message.answer("👤 Введите username (3-20 символов):")


@router.message(AuthStates.waiting_for_register_username)
async def get_register_username(message: Message, state: FSMContext):
    """Получение username для регистрации"""
    await state.update_data(username=message.text)
    await state.set_state(AuthStates.waiting_for_register_password)
    await message.answer("🔑 Введите пароль (минимум 6 символов):")


@router.message(AuthStates.waiting_for_register_password)
async def get_register_password(message: Message, state: FSMContext):
    """Получение пароля и регистрация"""
    data = await state.get_data()
    email = data.get("email")
    username = data.get("username")
    password = message.text
    
    db = SessionLocal()
    try:
        success, msg = register_user(db, message.from_user.id, email, username, password)
        
        if success:
            await message.answer(msg + "\n\n🔐 Теперь авторизуйтесь", reply_markup=get_start_keyboard())
        else:
            await message.answer(msg, reply_markup=get_start_keyboard())
    finally:
        db.close()
    
    await state.clear()
