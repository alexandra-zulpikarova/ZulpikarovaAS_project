import asyncio
import logging
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os

# Импорт системы чекбоксов
try:
    from checkbox_system import setup_checkbox_handlers, handle_checkbox_callbacks
    CHECKBOX_AVAILABLE = True
except ImportError:
    CHECKBOX_AVAILABLE = False
    print("⚠️ Модуль checkbox_system не найден. Функция магазина недоступна.")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Создание экземпляра бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Хранилище данных пользователей (в реальном проекте используйте базу данных)
user_data: Dict[int, Dict[str, Any]] = {}

# Состояния для FSM
class UserStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_feedback = State()
    quiz_in_progress = State()
    calculator_input = State()
    note_input = State()

# Данные для викторины
QUIZ_DATA = [
    {
        "question": "Какой язык программирования использует этот бот?",
        "options": ["JavaScript", "Python", "Java", "C++"],
        "correct": 1,
        "explanation": "Этот бот написан на Python с использованием библиотеки aiogram!"
    },
    {
        "question": "Что означает API?",
        "options": ["Application Programming Interface", "Automatic Program Installation", "Advanced Program Integration", "Application Process Information"],
        "correct": 0,
        "explanation": "API (Application Programming Interface) - это интерфейс программирования приложений."
    },
    {
        "question": "Сколько битов в одном байте?",
        "options": ["4", "8", "16", "32"],
        "correct": 1,
        "explanation": "В одном байте содержится 8 битов."
    }
]

# Получение или создание профиля пользователя
def get_user_profile(user_id: int) -> Dict[str, Any]:
    if user_id not in user_data:
        user_data[user_id] = {
            "name": None,
            "registration_date": datetime.now(),
            "quiz_score": 0,
            "quiz_attempts": 0,
            "notes": [],
            "last_activity": datetime.now()
        }
    user_data[user_id]["last_activity"] = datetime.now()
    return user_data[user_id]

# Главное меню
def get_main_menu() -> InlineKeyboardMarkup:
    keyboard_rows = [
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
         InlineKeyboardButton(text="🎮 Игры", callback_data="games")],
        [InlineKeyboardButton(text="🧮 Калькулятор", callback_data="calculator"),
         InlineKeyboardButton(text="📝 Заметки", callback_data="notes")],
        [InlineKeyboardButton(text="🌤 Погода", callback_data="weather"),
         InlineKeyboardButton(text="🎲 Случайное", callback_data="random")]
    ]
    
    # Добавляем кнопку магазина, если доступна система чекбоксов
    if CHECKBOX_AVAILABLE:
        keyboard_rows.append([InlineKeyboardButton(text="🛍 Магазин", callback_data="show_shop")])
    
    keyboard_rows.extend([
        [InlineKeyboardButton(text="💬 Отзыв", callback_data="feedback"),
         InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = message.from_user
    profile = get_user_profile(user.id)
    
    name = profile.get("name") or user.first_name or "Пользователь"
    
    shop_text = "\n• 🛍 Интерактивный магазин с чекбоксами" if CHECKBOX_AVAILABLE else ""
    
    welcome_text = f"""
🎉 Добро пожаловать, {name}!

🤖 Я — многофункциональный Telegram бот с множеством возможностей:

✨ <b>Основные функции:</b>
• 👤 Персональный профиль
• 🎮 Интерактивные игры и викторины
• 🧮 Встроенный калькулятор
• 📝 Система заметок
• 🌤 Информация о погоде
• 🎲 Развлекательный контент{shop_text}

Выберите интересующий раздел:
"""
    
    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode="HTML")

# Обработчики callback запросов
@dp.callback_query()
async def handle_callbacks(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    profile = get_user_profile(user_id)
    
    if callback.data == "profile":
        await show_profile(callback, profile)
    elif callback.data == "games":
        await show_games_menu(callback)
    elif callback.data == "calculator":
        await show_calculator(callback, state)
    elif callback.data == "notes":
        await show_notes_menu(callback, profile)
    elif callback.data == "weather":
        await show_weather(callback)
    elif callback.data == "random":
        await show_random_content(callback)
    elif callback.data == "feedback":
        await start_feedback(callback, state)
    elif callback.data == "help":
        await show_help(callback)
    elif callback.data == "main_menu":
        await show_main_menu(callback)
    elif callback.data == "start_quiz":
        await start_quiz(callback, state)
    elif callback.data.startswith("quiz_answer_"):
        await process_quiz_answer(callback, state)
    elif callback.data == "add_note":
        await start_add_note(callback, state)
    elif callback.data.startswith("delete_note_"):
        await delete_note(callback)
    elif CHECKBOX_AVAILABLE and any(callback.data.startswith(prefix) for prefix in [
        "show_shop", "category_", "back_to_categories", "show_cart",
        "toggle_", "qty_", "remove_", "clear_cart", "confirm_order"
    ]):
        # Передаем обработку системе чекбоксов
        await handle_checkbox_callbacks(callback, state)

async def show_profile(callback: CallbackQuery, profile: Dict[str, Any]):
    user = callback.from_user
    name = profile.get("name") or user.first_name or "Не указано"
    reg_date = profile["registration_date"].strftime("%d.%m.%Y")
    quiz_score = profile["quiz_score"]
    quiz_attempts = profile["quiz_attempts"]
    notes_count = len(profile["notes"])
    
    profile_text = f"""
👤 <b>Ваш профиль</b>

📛 Имя: {name}
🆔 ID: {user.id}
📅 Регистрация: {reg_date}

📊 <b>Статистика:</b>
🏆 Очки викторины: {quiz_score}
🎯 Попыток викторины: {quiz_attempts}
📝 Заметок: {notes_count}
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить имя", callback_data="change_name")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(profile_text, reply_markup=keyboard, parse_mode="HTML")

async def show_games_menu(callback: CallbackQuery):
    games_text = """
🎮 <b>Игры и развлечения</b>

Выберите игру:
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 Викторина", callback_data="start_quiz")],
        [InlineKeyboardButton(text="🎲 Кости", callback_data="dice_game")],
        [InlineKeyboardButton(text="🃏 Случайная карта", callback_data="random_card")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(games_text, reply_markup=keyboard, parse_mode="HTML")

async def start_quiz(callback: CallbackQuery, state: FSMContext):
    question_data = random.choice(QUIZ_DATA)
    
    await state.set_state(UserStates.quiz_in_progress)
    await state.update_data(
        current_question=question_data,
        quiz_score=0
    )
    
    options_keyboard = []
    for i, option in enumerate(question_data["options"]):
        options_keyboard.append([InlineKeyboardButton(
            text=f"{chr(65+i)}. {option}", 
            callback_data=f"quiz_answer_{i}"
        )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=options_keyboard)
    
    quiz_text = f"""
🧠 <b>Викторина</b>

❓ {question_data['question']}

Выберите правильный ответ:
"""
    
    await callback.message.edit_text(quiz_text, reply_markup=keyboard, parse_mode="HTML")

async def process_quiz_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    question = data["current_question"]
    answer_index = int(callback.data.split("_")[-1])
    
    user_id = callback.from_user.id
    profile = get_user_profile(user_id)
    
    is_correct = answer_index == question["correct"]
    
    if is_correct:
        profile["quiz_score"] += 10
        result_text = "✅ Правильно!"
        emoji = "🎉"
    else:
        result_text = "❌ Неправильно!"
        emoji = "😔"
    
    profile["quiz_attempts"] += 1
    
    result_message = f"""
{emoji} <b>{result_text}</b>

💡 {question['explanation']}

🏆 Ваши очки: {profile['quiz_score']}
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Еще вопрос", callback_data="start_quiz")],
        [InlineKeyboardButton(text="🎮 Игры", callback_data="games")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await state.clear()
    await callback.message.edit_text(result_message, reply_markup=keyboard, parse_mode="HTML")

async def show_calculator(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.calculator_input)
    
    calc_text = """
🧮 <b>Калькулятор</b>

Введите математическое выражение:
Примеры: 2+2, 10*5, 100/4, 2**3

Поддерживаемые операции: +, -, *, /, **, (), sqrt(), sin(), cos()
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(calc_text, reply_markup=keyboard, parse_mode="HTML")

async def show_notes_menu(callback: CallbackQuery, profile: Dict[str, Any]):
    notes = profile["notes"]
    
    if not notes:
        notes_text = """
📝 <b>Ваши заметки</b>

У вас пока нет заметок.
"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить заметку", callback_data="add_note")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ])
    else:
        notes_text = "📝 <b>Ваши заметки</b>\n\n"
        keyboard_buttons = []
        
        for i, note in enumerate(notes[-5:]):  # Показываем последние 5 заметок
            date = note["date"].strftime("%d.%m")
            text_preview = note["text"][:30] + "..." if len(note["text"]) > 30 else note["text"]
            notes_text += f"{i+1}. [{date}] {text_preview}\n"
            
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"🗑 Удалить заметку {i+1}", 
                callback_data=f"delete_note_{len(notes)-5+i}"
            )])
        
        keyboard_buttons.extend([
            [InlineKeyboardButton(text="➕ Добавить заметку", callback_data="add_note")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(notes_text, reply_markup=keyboard, parse_mode="HTML")

async def start_add_note(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.note_input)
    
    note_text = """
📝 <b>Новая заметка</b>

Введите текст заметки:
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="notes")]
    ])
    
    await callback.message.edit_text(note_text, reply_markup=keyboard, parse_mode="HTML")

async def delete_note(callback: CallbackQuery):
    user_id = callback.from_user.id
    profile = get_user_profile(user_id)
    note_index = int(callback.data.split("_")[-1])
    
    if 0 <= note_index < len(profile["notes"]):
        del profile["notes"][note_index]
        await callback.answer("✅ Заметка удалена!")
        await show_notes_menu(callback, profile)
    else:
        await callback.answer("❌ Заметка не найдена!")

async def show_weather(callback: CallbackQuery):
    weather_text = """
🌤 <b>Информация о погоде</b>

🌡 Сегодня: 22°C, солнечно ☀️
💨 Ветер: 5 м/с
💧 Влажность: 65%
👁 Видимость: 10 км

📅 Прогноз на завтра: 20°C, облачно ☁️

<i>Примечание: Это демо-данные. В реальном боте здесь будет API погоды.</i>
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="weather")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(weather_text, reply_markup=keyboard, parse_mode="HTML")

async def show_random_content(callback: CallbackQuery):
    content_type = random.choice(["fact", "quote", "number"])
    
    if content_type == "fact":
        facts = [
            "🧠 Человеческий мозг содержит около 86 миллиардов нейронов",
            "🌍 Земля вращается со скоростью около 1600 км/ч на экваторе",
            "🐙 У осьминогов три сердца и голубая кровь",
            "☀️ Свет от Солнца до Земли идет примерно 8 минут",
            "🦆 Кряканье утки не имеет эха"
        ]
        content = f"💡 <b>Интересный факт:</b>\n\n{random.choice(facts)}"
    
    elif content_type == "quote":
        quotes = [
            "\"Единственный способ сделать отличную работу — любить то, что ты делаешь.\" — Стив Джобс",
            "\"Жизнь — это то, что происходит, пока ты строишь планы.\" — Джон Леннон",
            "\"Будь собой. Остальные роли уже заняты.\" — Оскар Уайльд",
            "\"Образование — самое мощное оружие для изменения мира.\" — Нельсон Мандела"
        ]
        content = f"💭 <b>Мудрая мысль:</b>\n\n{random.choice(quotes)}"
    
    else:  # number
        number = random.randint(1, 1000)
        content = f"🔢 <b>Ваше случайное число:</b>\n\n{number}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Еще раз", callback_data="random")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(content, reply_markup=keyboard, parse_mode="HTML")

async def start_feedback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.waiting_for_feedback)
    
    feedback_text = """
💬 <b>Обратная связь</b>

Мы ценим ваше мнение! Напишите:
• Отзыв о боте
• Предложения по улучшению
• Сообщение об ошибке
• Идеи новых функций

Введите ваше сообщение:
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(feedback_text, reply_markup=keyboard, parse_mode="HTML")

async def show_help(callback: CallbackQuery):
    help_text = """
📚 <b>Справка</b>

🎯 <b>Основные функции:</b>

👤 <b>Профиль</b> — ваша персональная информация и статистика

🎮 <b>Игры</b> — викторины и мини-игры
• Викторина с вопросами на знания
• Зарабатывайте очки за правильные ответы

🧮 <b>Калькулятор</b> — решение математических выражений
• Базовые операции: +, -, *, /
• Степени: **
• Скобки для приоритета

📝 <b>Заметки</b> — сохранение важной информации
• Добавление заметок
• Просмотр последних записей
• Удаление ненужных заметок

🌤 <b>Погода</b> — информация о текущей погоде

🎲 <b>Случайное</b> — развлекательный контент
• Интересные факты
• Мудрые цитаты
• Случайные числа

💬 <b>Обратная связь</b> — связь с разработчиками

📱 <b>Команды:</b>
/start — перезапуск бота
/help — показать справку{f'\n/shop — открыть магазин' if CHECKBOX_AVAILABLE else ''}
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(help_text, reply_markup=keyboard, parse_mode="HTML")

async def show_main_menu(callback: CallbackQuery):
    user = callback.from_user
    profile = get_user_profile(user.id)
    name = profile.get("name") or user.first_name or "Пользователь"
    
    welcome_text = f"""
🏠 <b>Главное меню</b>

Привет, {name}! 👋

Выберите нужный раздел:
"""
    
    await callback.message.edit_text(welcome_text, reply_markup=get_main_menu(), parse_mode="HTML")

# Обработчики состояний
@dp.message(UserStates.calculator_input)
async def process_calculator_input(message: Message, state: FSMContext):
    expression = message.text.strip()
    
    try:
        # Безопасная обработка математических выражений
        import math
        allowed_names = {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "log": math.log, "exp": math.exp,
            "pi": math.pi, "e": math.e
        }
        
        # Удаляем потенциально опасные символы
        safe_expression = ''.join(c for c in expression if c in '0123456789+-*/().sincostanqrlgexpix ')
        
        result = eval(safe_expression, {"__builtins__": {}}, allowed_names)
        
        result_text = f"""
🧮 <b>Результат:</b>

📝 Выражение: `{expression}`
✅ Результат: `{result}`
"""
        
    except Exception as e:
        result_text = f"""
❌ <b>Ошибка вычисления:</b>

📝 Выражение: `{expression}`
🚫 Ошибка: Неверное выражение

💡 Проверьте синтаксис и попробуйте снова.
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧮 Новое вычисление", callback_data="calculator")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await state.clear()
    await message.answer(result_text, reply_markup=keyboard, parse_mode="HTML")

@dp.message(UserStates.note_input)
async def process_note_input(message: Message, state: FSMContext):
    note_text = message.text.strip()
    
    if len(note_text) > 1000:
        await message.answer("❌ Заметка слишком длинная (максимум 1000 символов). Попробуйте сократить.")
        return
    
    user_id = message.from_user.id
    profile = get_user_profile(user_id)
    
    note = {
        "text": note_text,
        "date": datetime.now()
    }
    
    profile["notes"].append(note)
    
    # Ограничиваем количество заметок (максимум 20)
    if len(profile["notes"]) > 20:
        profile["notes"] = profile["notes"][-20:]
    
    result_text = f"""
✅ <b>Заметка сохранена!</b>

📝 Текст: {note_text[:100]}{'...' if len(note_text) > 100 else ''}
📅 Дата: {note['date'].strftime('%d.%m.%Y %H:%M')}

📊 Всего заметок: {len(profile['notes'])}
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Мои заметки", callback_data="notes")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await state.clear()
    await message.answer(result_text, reply_markup=keyboard, parse_mode="HTML")

@dp.message(UserStates.waiting_for_feedback)
async def process_feedback(message: Message, state: FSMContext):
    feedback = message.text
    user_id = message.from_user.id
    
    # Сохраняем отзыв (в реальном проекте — в базу данных)
    logger.info(f"Feedback from user {user_id}: {feedback}")
    
    result_text = """
✅ <b>Спасибо за обратную связь!</b>

Ваше сообщение получено и будет рассмотрено разработчиками.

🙏 Мы ценим ваше мнение и работаем над улучшением бота!
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await state.clear()
    await message.answer(result_text, reply_markup=keyboard, parse_mode="HTML")

# Обработчик всех остальных сообщений
@dp.message()
async def handle_text(message: Message):
    text = message.text.lower() if message.text else ""
    
    # Простые ответы на популярные вопросы
    if any(word in text for word in ['привет', 'hello', 'hi', 'здравствуй']):
        await message.answer("👋 Привет! Используйте /start для доступа к меню.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ]))
    elif any(word in text for word in ['спасибо', 'thanks']):
        await message.answer("🙏 Пожалуйста! Рад помочь!")
    else:
        responses = [
            "🤔 Интересно! Попробуйте воспользоваться меню /start",
            "💡 Для доступа ко всем функциям используйте /start",
            "✨ Нажмите /start чтобы открыть главное меню бота"
        ]
        
        response = random.choice(responses)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ])
        await message.answer(response, reply_markup=keyboard)

# Главная функция
async def main():
    print("🤖 Запуск расширенного Telegram бота...")
    print(f"🔑 Токен: {'✅ Настроен' if BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE' else '❌ НЕ НАСТРОЕН!'}")
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n❌ ОШИБКА: Токен бота не настроен!")
        print("📝 Получите токен у @BotFather в Telegram")
        print("🔧 Установите переменную окружения: export BOT_TOKEN='ваш_токен'")
        return
    
    try:
        # Настройка обработчиков системы чекбоксов
        if CHECKBOX_AVAILABLE:
            setup_checkbox_handlers(dp)
            print("🛍 Система магазина с чекбоксами активирована")
        
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Бот успешно запущен и готов к работе!")
        print("📱 Найдите бота в Telegram и отправьте команду /start")
        
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())