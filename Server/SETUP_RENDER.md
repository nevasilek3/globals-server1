# 🚀 Полная инструкция по развертыванию на Render.com

## 📋 Шаг 1: Создание PostgreSQL базы данных на Render

### 1.1 Перейдите на render.com
- Откройте https://render.com
- Войдите в аккаунт (или создайте новый)

### 1.2 Создайте PostgreSQL сервис
1. Нажмите кнопку **"New +"** в левом меню
2. Выберите **"PostgreSQL"**
3. Заполните параметры:
   - **Name**: `cloud-dlc-db` (или любое имя)
   - **Database**: `cloud_dlc_db`
   - **User**: `cloud_dlc_user`
   - **Region**: выберите ближайший регион
   - **PostgreSQL Version**: 15 (или новее)
4. Нажмите **"Create Database"**

### 1.3 Получите строку подключения
После создания БД вы увидите экран с информацией:
- Скопируйте **Internal Database URL** (начинается с `postgresql://`)
- Это будет ваш `DATABASE_URL`

**Пример:**
```
postgresql://cloud_dlc_user:password123@dpg-xxxxx.render.internal:5432/cloud_dlc_db
```

---

## 📋 Шаг 2: Подготовка кода к развертыванию

### 2.1 Обновите файл `.env`

Создайте файл `Server/.env` с вашими данными:

```env
BOT_TOKEN=8784838245:AAGEPzmdV0YsampdTKvUvwJgSXtCfzoW-cg
DATABASE_URL=postgresql://cloud_dlc_user:password123@dpg-xxxxx.render.internal:5432/cloud_dlc_db
RENDER_EXTERNAL_URL=https://globals-server1.onrender.com
SERVER_PORT=8000
```

### 2.2 Убедитесь, что все файлы на месте

```
Server/
├── main.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
├── Procfile
├── database/
│   ├── __init__.py
│   ├── db.py
│   └── models.py
├── handlers/
│   ├── __init__.py
│   ├── start.py
│   ├── auth.py
│   ├── profile.py
│   └── keyboards.py
├── utils/
│   ├── __init__.py
│   ├── auth.py
│   ├── validators.py
│   └── pinger.py
├── api/
│   ├── __init__.py
│   └── routes.py
└── scripts/
    ├── __init__.py
    └── generate_keys.py
```

---

## 📋 Шаг 3: Развертывание на Render

### 3.1 Подготовьте GitHub репозиторий

1. Инициализируйте Git (если еще не сделали):
```bash
git init
git add .
git commit -m "Initial commit"
```

2. Создайте репозиторий на GitHub
3. Загрузите код:
```bash
git remote add origin https://github.com/your-username/your-repo.git
git branch -M main
git push -u origin main
```

### 3.2 Создайте Web Service на Render

1. На render.com нажмите **"New +"** → **"Web Service"**
2. Выберите **"Connect a repository"** и подключите ваш GitHub репозиторий
3. Заполните параметры:

| Параметр | Значение |
|----------|----------|
| **Name** | `cloud-dlc-bot` |
| **Environment** | `Python 3` |
| **Build Command** | `cd Server && pip install -r requirements.txt` |
| **Start Command** | `cd Server && python main.py` |
| **Plan** | `Free` |

### 3.3 Добавьте переменные окружения

1. Прокрутите вниз до раздела **"Environment"**
2. Нажмите **"Add Environment Variable"** и добавьте:

```
BOT_TOKEN = 8784838245:AAGEPzmdV0YsampdTKvUvwJgSXtCfzoW-cg
DATABASE_URL = postgresql://cloud_dlc_user:password123@dpg-xxxxx.render.internal:5432/cloud_dlc_db
RENDER_EXTERNAL_URL = https://globals-server1.onrender.com
SERVER_PORT = 8000
```

### 3.4 Запустите развертывание

1. Нажмите **"Create Web Service"**
2. Ждите завершения развертывания (обычно 2-5 минут)
3. Когда статус станет **"Live"**, ваш сервер готов!

---

## 📋 Шаг 4: Инициализация базы данных

### 4.1 Подключитесь к БД через Render

1. Перейдите в PostgreSQL сервис на Render
2. Нажмите **"Connect"**
3. Скопируйте **"PSQL Command"**
4. Выполните в терминале:

```bash
psql postgresql://cloud_dlc_user:password123@dpg-xxxxx.render.internal:5432/cloud_dlc_db
```

### 4.2 Или используйте автоматическую инициализацию

Сервер автоматически создаст таблицы при первом запуске благодаря коду в `main.py`:

```python
init_db()  # Создает все таблицы
```

---

## 📋 Шаг 5: Генерация API ключей

### 5.1 Локально (для тестирования)

```bash
cd Server
python scripts/generate_keys.py --count 10 --days 30
```

Это создаст 10 ключей подписки на 30 дней.

### 5.2 На Render (через Shell)

1. Перейдите в Web Service на Render
2. Нажмите **"Shell"** в верхнем меню
3. Выполните:

```bash
cd Server
python scripts/generate_keys.py --count 10 --days 30
```

---

## 🧪 Шаг 6: Тестирование

### 6.1 Проверьте здоровье сервера

```bash
curl https://globals-server1.onrender.com/health
```

Должен вернуть: `OK`

### 6.2 Тестируйте API авторизации

```bash
curl -X POST https://globals-server1.onrender.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

### 6.3 Тестируйте Telegram бота

1. Найдите бота в Telegram по токену
2. Отправьте `/start`
3. Нажмите "Регистрация"
4. Заполните данные
5. Нажмите "Авторизация"

---

## 🔧 Шаг 7: Обновление лоадера

В файле `src/main.cpp` обновите API URL:

```javascript
const API_URL = 'https://globals-server1.onrender.com';
```

Скомпилируйте лоадер и тестируйте авторизацию.

---

## 📊 Структура БД

### Таблица `users`
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    pc_type VARCHAR(50),
    subscription_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица `api_keys`
```sql
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    key VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
```

### Таблица `subscriptions`
```sql
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    plan VARCHAR(50) NOT NULL,
    activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);
```

---

## 🐛 Решение проблем

### Ошибка: "Cannot connect to database"
- Проверьте `DATABASE_URL` в переменных окружения
- Убедитесь, что PostgreSQL сервис запущен на Render
- Проверьте, что IP адрес разрешен (обычно разрешено автоматически)

### Ошибка: "ModuleNotFoundError"
- Проверьте, что все зависимости в `requirements.txt`
- Убедитесь, что `Build Command` правильный

### Бот не отвечает
- Проверьте `BOT_TOKEN` в переменных окружения
- Проверьте логи в разделе "Logs" на Render
- Убедитесь, что сервер в статусе "Live"

### Сервер засыпает
- Автопингер должен работать каждые 10 минут
- Проверьте логи на наличие ошибок пингера

---

## 📞 Полезные команды

### Просмотр логов
```bash
# На Render в разделе "Logs"
# Или через CLI:
render logs --service-id=your-service-id
```

### Перезагрузка сервера
```bash
# На Render нажмите "Manual Deploy" → "Deploy latest commit"
```

### Подключение к БД локально
```bash
psql postgresql://cloud_dlc_user:password@dpg-xxxxx.render.internal:5432/cloud_dlc_db
```

---

## ✅ Чек-лист

- [ ] PostgreSQL БД создана на Render
- [ ] DATABASE_URL скопирована
- [ ] GitHub репозиторий создан и загружен
- [ ] Web Service создан на Render
- [ ] Переменные окружения добавлены
- [ ] Сервер развернут (статус "Live")
- [ ] БД инициализирована
- [ ] API ключи сгенерированы
- [ ] Лоадер обновлен с новым API_URL
- [ ] Тестирование пройдено

---

## 🎉 Готово!

Ваш сервер теперь работает на Render.com и готов к использованию!

**Ссылка на сервер:** https://globals-server1.onrender.com
**Telegram бот:** @your_bot_username
**API:** https://globals-server1.onrender.com/api
