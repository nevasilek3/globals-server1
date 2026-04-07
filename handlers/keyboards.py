from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_start_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура при /start"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔐 Авторизация")],
            [KeyboardButton(text="📝 Регистрация")],
        ],
        resize_keyboard=True
    )


def get_profile_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура профиля после авторизации"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💳 Купить/Продлить подписку")],
            [KeyboardButton(text="🔑 Ввести ключ")],
            [KeyboardButton(text="🔄 Сбросить VDS")],
            [KeyboardButton(text="🚪 Выйти")],
        ],
        resize_keyboard=True
    )


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора подписки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="7 дней - 100₽", callback_data="sub_7_days")],
            [InlineKeyboardButton(text="30 дней - 350₽", callback_data="sub_30_days")],
            [InlineKeyboardButton(text="90 дней - 900₽", callback_data="sub_90_days")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_sub")],
        ]
    )
