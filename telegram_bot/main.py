import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота (получите у @BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Создание экземпляра бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния для FSM (конечный автомат состояний)
class UserStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_feedback = State()

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_name = message.from_user.first_name or "Пользователь"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Начать знакомство", callback_data="start_intro")],
        [InlineKeyboardButton(text="ℹ️ О боте", callback_data="about_bot")],
        [InlineKeyboardButton(text="📞 Помощь", callback_data="help")]
    ])
    
    welcome_text = f"""
🤖 Привет, {user_name}! 

Добро пожаловать в наш умный чат-бот! 

Я могу помочь вам с:
• Ответами на вопросы
• Полезной информацией
• Развлечениями и играми
• Обратной связью

Выберите действие ниже:
"""
    
    await message.answer(welcome_text, reply_markup=keyboard)

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
📚 <b>Список команд:</b>

/start - Главное меню
/help - Показать это сообщение
/profile - Мой профиль
/feedback - Оставить отзыв
/joke - Случайная шутка
/weather - Узнать погоду
/time - Текущее время

💡 <b>Возможности:</b>
• Интерактивное меню
• Обратная связь
• Развлекательный контент
• Персональные настройки

Если у вас есть вопросы, просто напишите мне!
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await message.answer(help_text, parse_mode="HTML", reply_markup=keyboard)

# Обработчик команды /profile
@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    user = message.from_user
    profile_text = f"""
👤 <b>Ваш профиль:</b>

📛 Имя: {user.first_name or 'Не указано'}
📛 Фамилия: {user.last_name or 'Не указано'}
🆔 ID: {user.id}
📱 Username: @{user.username or 'Не указан'}
🌐 Язык: {user.language_code or 'Не определен'}

📅 Дата регистрации в боте: {datetime.now().strftime('%d.%m.%Y')}
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить имя", callback_data="change_name")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await message.answer(profile_text, parse_mode="HTML", reply_markup=keyboard)

# Обработчик команды /feedback
@dp.message(Command("feedback"))
async def cmd_feedback(message: Message, state: FSMContext):
    await state.set_state(UserStates.waiting_for_feedback)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_feedback")]
    ])
    
    await message.answer(
        "✍️ Напишите ваш отзыв или предложение:",
        reply_markup=keyboard
    )

# Обработчик команды /joke
@dp.message(Command("joke"))
async def cmd_joke(message: Message):
    jokes = [
        "Почему программисты не любят природу? Там слишком много багов! 🐛",
        "Что такое рекурсия? Смотри что такое рекурсия 🔄",
        "Программист — это человек, который решает проблемы, о существовании которых вы не подозревали, способами, которых вы не понимаете 💻",
        "Есть только 10 типов людей в мире: те, кто понимают двоичную систему, и те, кто не понимают 😄",
        "Программист без кофе — это спящий программист ☕"
    ]
    
    import random
    joke = random.choice(jokes)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😂 Еще шутку!", callback_data="another_joke")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await message.answer(f"😄 {joke}", reply_markup=keyboard)

# Обработчик команды /time
@dp.message(Command("time"))
async def cmd_time(message: Message):
    current_time = datetime.now().strftime("%H:%M:%S %d.%m.%Y")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить время", callback_data="update_time")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await message.answer(f"🕐 Текущее время: {current_time}", reply_markup=keyboard)

# Обработчики callback запросов
@dp.callback_query()
async def handle_callbacks(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    if callback.data == "start_intro":
        await state.set_state(UserStates.waiting_for_name)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Пропустить", callback_data="skip_intro")]
        ])
        
        await callback.message.edit_text(
            "👋 Как вас зовут? Напишите ваше имя:",
            reply_markup=keyboard
        )
    
    elif callback.data == "about_bot":
        about_text = """
🤖 <b>О боте</b>

Этот бот создан для демонстрации возможностей Telegram Bot API с использованием библиотеки aiogram.

✨ <b>Особенности:</b>
• Современный интерфейс
• Интерактивные кнопки
• Система состояний
• Обработка текстовых сообщений
• Персонализация

🔧 <b>Технологии:</b>
• Python 3.8+
• aiogram 3.x
• asyncio

Версия: 1.0.0
"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ])
        
        await callback.message.edit_text(about_text, parse_mode="HTML", reply_markup=keyboard)
    
    elif callback.data == "help":
        await cmd_help(callback.message)
    
    elif callback.data == "main_menu":
        user_name = callback.from_user.first_name or "Пользователь"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Начать знакомство", callback_data="start_intro")],
            [InlineKeyboardButton(text="ℹ️ О боте", callback_data="about_bot")],
            [InlineKeyboardButton(text="📞 Помощь", callback_data="help")]
        ])
        
        welcome_text = f"""
🤖 Привет, {user_name}! 

Добро пожаловать в наш умный чат-бот! 

Я могу помочь вам с:
• Ответами на вопросы
• Полезной информацией
• Развлечениями и играми
• Обратной связью

Выберите действие ниже:
"""
        
        await callback.message.edit_text(welcome_text, reply_markup=keyboard)
    
    elif callback.data == "change_name":
        await state.set_state(UserStates.waiting_for_name)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_name_change")]
        ])
        
        await callback.message.edit_text(
            "✏️ Введите новое имя:",
            reply_markup=keyboard
        )
    
    elif callback.data == "cancel_feedback":
        await state.clear()
        await callback.message.edit_text("❌ Отправка отзыва отменена.")
    
    elif callback.data == "cancel_name_change":
        await state.clear()
        await callback.message.edit_text("❌ Изменение имени отменено.")
    
    elif callback.data == "skip_intro":
        await state.clear()
        await callback.message.edit_text("✅ Знакомство пропущено. Добро пожаловать!")
    
    elif callback.data == "another_joke":
        await cmd_joke(callback.message)
    
    elif callback.data == "update_time":
        await cmd_time(callback.message)

# Обработчик состояния ожидания имени
@dp.message(UserStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    
    if len(name) > 50:
        await message.answer("❌ Имя слишком длинное. Попробуйте еще раз (максимум 50 символов):")
        return
    
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await message.answer(
        f"✅ Приятно познакомиться, {name}! Теперь я буду обращаться к вам по имени.",
        reply_markup=keyboard
    )

# Обработчик состояния ожидания отзыва
@dp.message(UserStates.waiting_for_feedback)
async def process_feedback(message: Message, state: FSMContext):
    feedback = message.text
    
    # Здесь можно сохранить отзыв в базу данных
    logger.info(f"Получен отзыв от пользователя {message.from_user.id}: {feedback}")
    
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await message.answer(
        "✅ Спасибо за ваш отзыв! Мы обязательно его рассмотрим.",
        reply_markup=keyboard
    )

# Обработчик всех остальных текстовых сообщений
@dp.message()
async def handle_text(message: Message):
    text = message.text.lower()
    
    # Простые ответы на популярные вопросы
    if any(word in text for word in ['привет', 'hello', 'hi', 'здравствуй']):
        await message.answer("👋 Привет! Как дела?")
    elif any(word in text for word in ['как дела', 'как дела?', 'how are you']):
        await message.answer("😊 У меня все отлично! А у вас как?")
    elif any(word in text for word in ['спасибо', 'thanks', 'thank you']):
        await message.answer("🙏 Пожалуйста! Рад помочь!")
    elif any(word in text for word in ['пока', 'bye', 'goodbye']):
        await message.answer("👋 До свидания! Возвращайтесь еще!")
    else:
        # Эхо для неизвестных сообщений
        responses = [
            "🤔 Интересно! Расскажите больше.",
            "💭 Понимаю вас. Что еще вас интересует?",
            "🎯 Хороший вопрос! Попробуйте воспользоваться командами /help",
            "✨ Спасибо за сообщение! Используйте /start для главного меню."
        ]
        
        import random
        response = random.choice(responses)
        await message.answer(response)

# Главная функция
async def main():
    print("🤖 Запуск Telegram бота...")
    print(f"🔑 Токен: {'Настроен' if BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE' else 'НЕ НАСТРОЕН!'}")
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ОШИБКА: Установите токен бота в переменную окружения BOT_TOKEN")
        print("📝 Получите токен у @BotFather в Telegram")
        return
    
    try:
        # Удаляем вебхуки (если были)
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Бот успешно запущен!")
        
        # Запускаем поллинг
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())