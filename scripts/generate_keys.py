"""
Скрипт для генерации API ключей подписки

Использование:
    python scripts/generate_keys.py --count 10 --days 30
"""

import sys
import secrets
import argparse
from datetime import datetime, timedelta
from database.db import SessionLocal
from database.models import ApiKey

sys.path.insert(0, '.')


def generate_key() -> str:
    """Генерирует уникальный API ключ"""
    return secrets.token_urlsafe(32)


def create_keys(count: int = 10, days: int = 30):
    """Создает N ключей подписки"""
    db = SessionLocal()
    
    try:
        keys = []
        expires_at = datetime.utcnow() + timedelta(days=days)
        
        for i in range(count):
            key = generate_key()
            
            # Проверяем уникальность
            while db.query(ApiKey).filter(ApiKey.key == key).first():
                key = generate_key()
            
            api_key = ApiKey(
                user_id=0,  # 0 = ключ еще не активирован
                key=key,
                is_active=True,
                expires_at=expires_at
            )
            db.add(api_key)
            keys.append(key)
        
        db.commit()
        
        print(f"✅ Создано {count} ключей подписки на {days} дней")
        print(f"📅 Истекают: {expires_at.strftime('%d.%m.%Y')}\n")
        print("Ключи:")
        for i, key in enumerate(keys, 1):
            print(f"{i}. {key}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Генератор API ключей")
    parser.add_argument("--count", type=int, default=10, help="Количество ключей")
    parser.add_argument("--days", type=int, default=30, help="Дней действия")
    
    args = parser.parse_args()
    create_keys(args.count, args.days)
