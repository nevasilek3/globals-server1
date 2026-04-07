import bcrypt
from sqlalchemy.orm import Session
from database.models import User
from utils.validators import validate_email, validate_username, validate_password
from typing import Tuple, Optional


def hash_password(password: str) -> str:
    """Хеширует пароль"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Проверяет пароль"""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def register_user(db: Session, telegram_id: int, email: str, username: str, password: str) -> Tuple[bool, str]:
    """Регистрирует нового пользователя"""
    
    # Валидация
    if not validate_email(email):
        return False, "❌ Некорректный email"
    
    if not validate_username(username):
        return False, "❌ Username должен быть 3-20 символов (буквы, цифры, подчеркивание)"
    
    is_valid, msg = validate_password(password)
    if not is_valid:
        return False, f"❌ {msg}"
    
    # Проверка существования
    if db.query(User).filter(User.email == email).first():
        return False, "❌ Email уже зарегистрирован"
    
    if db.query(User).filter(User.username == username).first():
        return False, "❌ Username уже занят"
    
    # Создание пользователя
    try:
        user = User(
            telegram_id=telegram_id,
            email=email,
            username=username,
            password_hash=hash_password(password)
        )
        db.add(user)
        db.commit()
        return True, "✅ Регистрация успешна!"
    except Exception as e:
        db.rollback()
        return False, f"❌ Ошибка: {str(e)}"


def login_user(db: Session, username: str, password: str) -> Tuple[bool, Optional[User], str]:
    """Авторизует пользователя"""
    
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return False, None, "❌ Пользователь не найден"
    
    if not verify_password(password, user.password_hash):
        return False, None, "❌ Неверный пароль"
    
    return True, user, "✅ Авторизация успешна!"
