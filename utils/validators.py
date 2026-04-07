import re
from typing import Tuple


def validate_email(email: str) -> bool:
    """Проверка корректности email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> bool:
    """Проверка корректности username (3-20 символов, буквы, цифры, подчеркивание)"""
    if len(username) < 3 or len(username) > 20:
        return False
    pattern = r'^[a-zA-Z0-9_]+$'
    return re.match(pattern, username) is not None


def validate_password(password: str) -> Tuple[bool, str]:
    """Проверка пароля (минимум 6 символов)"""
    if len(password) < 6:
        return False, "Пароль должен быть минимум 6 символов"
    return True, "OK"
