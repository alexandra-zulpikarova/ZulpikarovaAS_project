# 🤖 Telegram Bot на Python

Многофункциональный Telegram бот с современным интерфейсом и множеством возможностей.

## ✨ Возможности

### 🎯 Основные функции:
- **👤 Персональный профиль** — информация о пользователе и статистика
- **🎮 Интерактивные игры** — викторины с системой очков
- **🧮 Встроенный калькулятор** — решение математических выражений
- **📝 Система заметок** — сохранение и управление заметками
- **🌤 Информация о погоде** — (демо-данные, легко интегрировать API)
- **🎲 Развлекательный контент** — факты, цитаты, случайные числа
- **💬 Обратная связь** — система отзывов от пользователей

### 🔧 Технические особенности:
- Асинхронная архитектура (asyncio)
- Конечный автомат состояний (FSM)
- Интерактивные inline-клавиатуры
- Безопасная обработка пользовательского ввода
- Система хранения данных пользователей
- Подробное логирование
- Обработка ошибок

## 📋 Требования

- Python 3.8+
- Токен Telegram бота от [@BotFather](https://t.me/botfather)

## 🚀 Быстрый старт

### 1. Клонирование и установка зависимостей

```bash
# Перейдите в папку проекта
cd telegram_bot

# Установите зависимости
pip install -r requirements.txt
```

### 2. Создание бота в Telegram

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Придумайте название и username для бота
4. Скопируйте полученный токен

### 3. Настройка токена

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл и укажите ваш токен:

```env
BOT_TOKEN=ваш_токен_от_botfather
```

Или установите переменную окружения:

```bash
export BOT_TOKEN="ваш_токен_от_botfather"
```

### 4. Запуск бота

#### Базовая версия:
```bash
python main.py
```

#### Расширенная версия (рекомендуется):
```bash
python advanced_bot.py
```

## 📁 Структура проекта

```
telegram_bot/
├── main.py              # Базовая версия бота
├── advanced_bot.py      # Расширенная версия с дополнительными функциями
├── requirements.txt     # Зависимости Python
├── .env.example        # Пример файла конфигурации
├── .env               # Ваша конфигурация (создайте сами)
└── README.md          # Данная документация
```

## 🎮 Функции бота

### 👤 Профиль пользователя
- Отображение персональной информации
- Статистика игр и активности
- Возможность изменения имени

### 🧠 Викторина
- Интерактивные вопросы с вариантами ответов
- Система очков за правильные ответы
- Статистика попыток и достижений

### 🧮 Калькулятор
- Базовые математические операции (+, -, *, /)
- Степени (**)
- Математические функции (sin, cos, sqrt)
- Безопасная обработка выражений

### 📝 Заметки
- Создание и сохранение заметок
- Просмотр последних записей
- Удаление ненужных заметок
- Ограничение по количеству (20 заметок)

### 🎲 Развлечения
- Интересные факты
- Мудрые цитаты
- Генерация случайных чисел

## 🔧 Настройка и расширение

### Добавление новых команд

```python
@dp.message(Command("новая_команда"))
async def новая_команда(message: Message):
    await message.answer("Ответ на новую команду")
```

### Добавление новых состояний

```python
class UserStates(StatesGroup):
    новое_состояние = State()

@dp.message(UserStates.новое_состояние)
async def обработать_новое_состояние(message: Message, state: FSMContext):
    # Обработка состояния
    await state.clear()
```

### Интеграция с базой данных

Для продакшена рекомендуется заменить словарь `user_data` на базу данных:

```python
# Пример с SQLite
import sqlite3

def init_db():
    conn = sqlite3.connect('bot_users.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            quiz_score INTEGER DEFAULT 0,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
```

### Добавление API погоды

Замените демо-данные в функции `show_weather()`:

```python
import aiohttp

async def get_weather(city="Moscow"):
    api_key = "ваш_api_ключ"
    async with aiohttp.ClientSession() as session:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
        async with session.get(url) as response:
            return await response.json()
```

## 🐛 Отладка и логирование

Бот ведет подробные логи всех операций. Для настройки уровня логирования:

```python
logging.basicConfig(level=logging.DEBUG)  # Подробные логи
logging.basicConfig(level=logging.INFO)   # Основная информация
logging.basicConfig(level=logging.ERROR)  # Только ошибки
```

## 📊 Мониторинг

Для продакшена рекомендуется добавить:

1. **Системы мониторинга** (Prometheus, Grafana)
2. **Обработку исключений** с уведомлениями
3. **Ограничения по частоте запросов** (rate limiting)
4. **Backup данных пользователей**

## 🚀 Деплой

### На VPS/сервере:

```bash
# Установка в фоновом режиме
nohup python advanced_bot.py &

# Или с помощью systemd
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### Docker:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "advanced_bot.py"]
```

### Heroku:

```bash
# Создание Procfile
echo "web: python advanced_bot.py" > Procfile

# Деплой
git push heroku main
```

## 🔒 Безопасность

- ✅ Токен бота хранится в переменных окружения
- ✅ Безопасная обработка математических выражений
- ✅ Валидация пользовательского ввода
- ✅ Ограничения на размер заметок
- ✅ Логирование подозрительной активности

## 📝 Лицензия

MIT License - используйте свободно для любых целей.

## 🤝 Поддержка

Если у вас есть вопросы или предложения:

1. Создайте Issue в репозитории
2. Напишите в Telegram: [@username](https://t.me/username)
3. Email: example@email.com

## 🎯 Планы развития

- [ ] Интеграция с базой данных
- [ ] API погоды
- [ ] Многоязычность
- [ ] Административная панель
- [ ] Статистика и аналитика
- [ ] Игры и развлечения
- [ ] Уведомления и напоминания
- [ ] Интеграция с внешними сервисами

---

**Удачи в разработке вашего Telegram бота! 🚀**