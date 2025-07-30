"""
Примеры расширений для Telegram бота
Этот файл содержит дополнительные функции, которые можно интегрировать в основной бот
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# =============================================
# 🌤 ИНТЕГРАЦИЯ С API ПОГОДЫ
# =============================================

async def get_real_weather(city: str = "Moscow", api_key: str = None):
    """
    Получение реальных данных о погоде через OpenWeatherMap API
    
    Для использования:
    1. Зарегистрируйтесь на https://openweathermap.org/api
    2. Получите API ключ
    3. Замените функцию show_weather() в основном боте
    """
    if not api_key:
        return None
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": api_key,
                "units": "metric",
                "lang": "ru"
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    weather_info = {
                        "city": data["name"],
                        "temperature": round(data["main"]["temp"]),
                        "feels_like": round(data["main"]["feels_like"]),
                        "description": data["weather"][0]["description"],
                        "humidity": data["main"]["humidity"],
                        "wind_speed": data["wind"]["speed"],
                        "icon": data["weather"][0]["icon"]
                    }
                    
                    return weather_info
                else:
                    return None
    except Exception as e:
        print(f"Ошибка получения погоды: {e}")
        return None

def format_weather_message(weather_data):
    """Форматирование сообщения о погоде"""
    if not weather_data:
        return "❌ Не удалось получить данные о погоде"
    
    weather_emoji = {
        "01d": "☀️", "01n": "🌙", "02d": "⛅", "02n": "☁️",
        "03d": "☁️", "03n": "☁️", "04d": "☁️", "04n": "☁️",
        "09d": "🌧️", "09n": "🌧️", "10d": "🌦️", "10n": "🌧️",
        "11d": "⛈️", "11n": "⛈️", "13d": "❄️", "13n": "❄️",
        "50d": "🌫️", "50n": "🌫️"
    }
    
    emoji = weather_emoji.get(weather_data["icon"], "🌤")
    
    return f"""
🌤 <b>Погода в {weather_data['city']}</b>

{emoji} {weather_data['temperature']}°C, {weather_data['description']}
🌡 Ощущается как: {weather_data['feels_like']}°C
💧 Влажность: {weather_data['humidity']}%
💨 Ветер: {weather_data['wind_speed']} м/с

📅 Обновлено: {datetime.now().strftime('%H:%M')}
"""

# =============================================
# 💾 ИНТЕГРАЦИЯ С БАЗОЙ ДАННЫХ SQLite
# =============================================

import sqlite3
from typing import Optional, List, Dict, Any

class BotDatabase:
    """Класс для работы с базой данных бота"""
    
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    quiz_score INTEGER DEFAULT 0,
                    quiz_attempts INTEGER DEFAULT 0,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    content TEXT NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            conn.commit()
    
    def get_or_create_user(self, user_data: Dict) -> Dict[str, Any]:
        """Получение или создание пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Проверяем существование пользователя
            user = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", 
                (user_data["id"],)
            ).fetchone()
            
            if user:
                # Обновляем активность
                conn.execute(
                    "UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (user_data["id"],)
                )
                return dict(user)
            else:
                # Создаем нового пользователя
                conn.execute("""
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                """, (user_data["id"], user_data.get("username"), 
                      user_data.get("first_name"), user_data.get("last_name")))
                
                conn.commit()
                
                # Возвращаем созданного пользователя
                user = conn.execute(
                    "SELECT * FROM users WHERE user_id = ?", 
                    (user_data["id"],)
                ).fetchone()
                return dict(user)
    
    def add_note(self, user_id: int, content: str) -> bool:
        """Добавление заметки"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO notes (user_id, content) VALUES (?, ?)",
                    (user_id, content)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка добавления заметки: {e}")
            return False
    
    def get_user_notes(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Получение заметок пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            notes = conn.execute("""
                SELECT * FROM notes 
                WHERE user_id = ? 
                ORDER BY created_date DESC 
                LIMIT ?
            """, (user_id, limit)).fetchall()
            
            return [dict(note) for note in notes]
    
    def delete_note(self, note_id: int, user_id: int) -> bool:
        """Удаление заметки"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute(
                    "DELETE FROM notes WHERE id = ? AND user_id = ?",
                    (note_id, user_id)
                )
                conn.commit()
                return result.rowcount > 0
        except Exception as e:
            print(f"Ошибка удаления заметки: {e}")
            return False
    
    def add_feedback(self, user_id: int, message: str) -> bool:
        """Добавление отзыва"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO feedback (user_id, message) VALUES (?, ?)",
                    (user_id, message)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка добавления отзыва: {e}")
            return False

# =============================================
# 🎮 ДОПОЛНИТЕЛЬНЫЕ ИГРЫ
# =============================================

import random

class GameEngine:
    """Игровой движок для мини-игр"""
    
    @staticmethod
    def number_guessing_game():
        """Игра 'Угадай число'"""
        number = random.randint(1, 100)
        attempts = 0
        max_attempts = 7
        
        return {
            "number": number,
            "attempts": attempts,
            "max_attempts": max_attempts,
            "status": "playing",
            "hint": f"Я загадал число от 1 до 100. У вас {max_attempts} попыток!"
        }
    
    @staticmethod
    def process_guess(game_data: Dict, guess: int) -> Dict:
        """Обработка попытки угадывания"""
        game_data["attempts"] += 1
        target = game_data["number"]
        
        if guess == target:
            game_data["status"] = "won"
            game_data["hint"] = f"🎉 Поздравляю! Вы угадали число {target} за {game_data['attempts']} попыток!"
        elif game_data["attempts"] >= game_data["max_attempts"]:
            game_data["status"] = "lost"
            game_data["hint"] = f"😔 Попытки закончились! Загаданное число было {target}"
        elif guess < target:
            game_data["hint"] = f"📈 Загаданное число больше {guess}. Попытка {game_data['attempts']}/{game_data['max_attempts']}"
        else:
            game_data["hint"] = f"📉 Загаданное число меньше {guess}. Попытка {game_data['attempts']}/{game_data['max_attempts']}"
        
        return game_data
    
    @staticmethod
    def rock_paper_scissors(user_choice: str) -> Dict:
        """Игра 'Камень, ножницы, бумага'"""
        choices = ["камень", "ножницы", "бумага"]
        bot_choice = random.choice(choices)
        
        win_conditions = {
            "камень": "ножницы",
            "ножницы": "бумага", 
            "бумага": "камень"
        }
        
        if user_choice == bot_choice:
            result = "Ничья!"
            emoji = "🤝"
        elif win_conditions[user_choice] == bot_choice:
            result = "Вы выиграли!"
            emoji = "🎉"
        else:
            result = "Вы проиграли!"
            emoji = "😔"
        
        return {
            "user_choice": user_choice,
            "bot_choice": bot_choice,
            "result": result,
            "emoji": emoji
        }

# =============================================
# 📊 СТАТИСТИКА И АНАЛИТИКА
# =============================================

class BotAnalytics:
    """Система аналитики бота"""
    
    def __init__(self, db: BotDatabase):
        self.db = db
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Получение статистики пользователя"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Основная информация
            user = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", 
                (user_id,)
            ).fetchone()
            
            # Количество заметок
            notes_count = conn.execute(
                "SELECT COUNT(*) as count FROM notes WHERE user_id = ?",
                (user_id,)
            ).fetchone()["count"]
            
            # Количество отзывов
            feedback_count = conn.execute(
                "SELECT COUNT(*) as count FROM feedback WHERE user_id = ?",
                (user_id,)
            ).fetchone()["count"]
            
            return {
                "user": dict(user) if user else None,
                "notes_count": notes_count,
                "feedback_count": feedback_count,
                "days_registered": (datetime.now() - datetime.fromisoformat(user["registration_date"])).days if user else 0
            }
    
    def get_global_stats(self) -> Dict:
        """Получение глобальной статистики"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Общее количество пользователей
            total_users = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()["count"]
            
            # Активные пользователи за последние 7 дней
            active_users = conn.execute("""
                SELECT COUNT(*) as count FROM users 
                WHERE last_activity >= datetime('now', '-7 days')
            """).fetchone()["count"]
            
            # Общее количество заметок
            total_notes = conn.execute("SELECT COUNT(*) as count FROM notes").fetchone()["count"]
            
            # Общее количество отзывов
            total_feedback = conn.execute("SELECT COUNT(*) as count FROM feedback").fetchone()["count"]
            
            return {
                "total_users": total_users,
                "active_users_7d": active_users,
                "total_notes": total_notes,
                "total_feedback": total_feedback
            }

# =============================================
# 🔔 СИСТЕМА УВЕДОМЛЕНИЙ
# =============================================

class NotificationSystem:
    """Система уведомлений и напоминаний"""
    
    def __init__(self, bot):
        self.bot = bot
        self.scheduled_notifications = []
    
    async def send_notification(self, user_id: int, message: str, keyboard=None):
        """Отправка уведомления пользователю"""
        try:
            await self.bot.send_message(user_id, message, reply_markup=keyboard)
            return True
        except Exception as e:
            print(f"Ошибка отправки уведомления: {e}")
            return False
    
    def schedule_notification(self, user_id: int, message: str, delay_seconds: int):
        """Планирование уведомления"""
        send_time = datetime.now() + timedelta(seconds=delay_seconds)
        
        notification = {
            "user_id": user_id,
            "message": message,
            "send_time": send_time,
            "sent": False
        }
        
        self.scheduled_notifications.append(notification)
        return notification
    
    async def process_scheduled_notifications(self):
        """Обработка запланированных уведомлений"""
        current_time = datetime.now()
        
        for notification in self.scheduled_notifications:
            if not notification["sent"] and current_time >= notification["send_time"]:
                success = await self.send_notification(
                    notification["user_id"], 
                    notification["message"]
                )
                
                if success:
                    notification["sent"] = True

# =============================================
# 🌍 МНОГОЯЗЫЧНОСТЬ
# =============================================

class Localization:
    """Система локализации"""
    
    def __init__(self):
        self.translations = {
            "ru": {
                "welcome": "Добро пожаловать!",
                "profile": "Профиль",
                "games": "Игры",
                "calculator": "Калькулятор",
                "notes": "Заметки",
                "weather": "Погода",
                "feedback": "Отзыв",
                "help": "Помощь",
                "main_menu": "Главное меню",
                "back": "Назад",
                "cancel": "Отмена"
            },
            "en": {
                "welcome": "Welcome!",
                "profile": "Profile",
                "games": "Games", 
                "calculator": "Calculator",
                "notes": "Notes",
                "weather": "Weather",
                "feedback": "Feedback",
                "help": "Help",
                "main_menu": "Main Menu",
                "back": "Back",
                "cancel": "Cancel"
            }
        }
    
    def get_text(self, key: str, lang: str = "ru") -> str:
        """Получение переведенного текста"""
        return self.translations.get(lang, {}).get(key, key)
    
    def get_keyboard(self, buttons: List[str], lang: str = "ru") -> InlineKeyboardMarkup:
        """Создание локализованной клавиатуры"""
        keyboard = []
        for button_key in buttons:
            text = self.get_text(button_key, lang)
            keyboard.append([InlineKeyboardButton(text=text, callback_data=button_key)])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

# =============================================
# 📈 СИСТЕМА РЕЙТИНГОВ
# =============================================

class RatingSystem:
    """Система рейтингов и достижений"""
    
    def __init__(self, db: BotDatabase):
        self.db = db
        self.achievements = {
            "first_note": {"name": "Первая заметка", "description": "Создайте первую заметку", "points": 10},
            "quiz_master": {"name": "Мастер викторины", "description": "Наберите 100 очков в викторине", "points": 50},
            "active_user": {"name": "Активный пользователь", "description": "Используйте бота 7 дней подряд", "points": 30},
            "feedback_giver": {"name": "Помощник", "description": "Оставьте отзыв", "points": 15}
        }
    
    def check_achievements(self, user_id: int) -> List[str]:
        """Проверка достижений пользователя"""
        stats = BotAnalytics(self.db).get_user_stats(user_id)
        unlocked = []
        
        # Проверка достижения "Первая заметка"
        if stats["notes_count"] >= 1:
            unlocked.append("first_note")
        
        # Проверка достижения "Мастер викторины"
        if stats["user"] and stats["user"]["quiz_score"] >= 100:
            unlocked.append("quiz_master")
        
        # Проверка достижения "Активный пользователь"
        if stats["days_registered"] >= 7:
            unlocked.append("active_user")
        
        # Проверка достижения "Помощник"
        if stats["feedback_count"] >= 1:
            unlocked.append("feedback_giver")
        
        return unlocked

# =============================================
# ПРИМЕР ИНТЕГРАЦИИ В ОСНОВНОЙ БОТ
# =============================================

"""
Пример интеграции расширений в основной бот:

# В начале файла добавить:
from extensions_example import BotDatabase, GameEngine, BotAnalytics, NotificationSystem

# Инициализация
db = BotDatabase()
analytics = BotAnalytics(db)
notifications = NotificationSystem(bot)

# В обработчике профиля заменить:
async def cmd_profile(message: Message):
    user_data = {
        "id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name
    }
    
    user_profile = db.get_or_create_user(user_data)
    stats = analytics.get_user_stats(message.from_user.id)
    
    # Форматирование и отправка профиля...

# В обработчике заметок заменить:
async def process_note_input(message: Message, state: FSMContext):
    success = db.add_note(message.from_user.id, message.text.strip())
    
    if success:
        await message.answer("✅ Заметка сохранена!")
    else:
        await message.answer("❌ Ошибка сохранения заметки")
"""