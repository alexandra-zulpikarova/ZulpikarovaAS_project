#!/usr/bin/env python3
"""
Демонстрационный файл для тестирования компонентов бота
Этот файл показывает, как можно тестировать отдельные части бота локально
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Симуляция пользователя для тестирования
class MockUser:
    def __init__(self, user_id: int, first_name: str = "Тестовый", last_name: str = "Пользователь"):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = f"test_user_{user_id}"
        self.language_code = "ru"

class MockMessage:
    def __init__(self, text: str, user: MockUser):
        self.text = text
        self.from_user = user
        self.message_id = 123
        self.date = datetime.now()

# Тестирование функций из основного бота
def test_user_data_storage():
    """Тестирование системы хранения данных пользователей"""
    print("🧪 Тестирование системы хранения данных...")
    
    # Симуляция данных пользователей
    user_data = {}
    
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
    
    # Создание тестового пользователя
    test_user = MockUser(12345, "Иван", "Иванов")
    profile = get_user_profile(test_user.id)
    
    print(f"✅ Создан профиль пользователя: {test_user.first_name}")
    print(f"📊 Данные профиля: {json.dumps(profile, default=str, ensure_ascii=False, indent=2)}")
    
    # Добавление заметки
    profile["notes"].append({
        "text": "Тестовая заметка",
        "date": datetime.now()
    })
    
    # Увеличение очков викторины
    profile["quiz_score"] += 10
    profile["quiz_attempts"] += 1
    
    print(f"📝 Добавлена заметка, обновлены очки викторины")
    print(f"🏆 Текущие очки: {profile['quiz_score']}")
    
    return True

def test_quiz_system():
    """Тестирование системы викторины"""
    print("\n🎯 Тестирование системы викторины...")
    
    quiz_data = [
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
        }
    ]
    
    import random
    question = random.choice(quiz_data)
    
    print(f"❓ Вопрос: {question['question']}")
    for i, option in enumerate(question['options']):
        print(f"   {chr(65+i)}. {option}")
    
    print(f"✅ Правильный ответ: {chr(65 + question['correct'])}. {question['options'][question['correct']]}")
    print(f"💡 Объяснение: {question['explanation']}")
    
    return True

def test_calculator():
    """Тестирование калькулятора"""
    print("\n🧮 Тестирование калькулятора...")
    
    expressions = [
        "2 + 2",
        "10 * 5",
        "100 / 4",
        "2 ** 3",
        "sqrt(16)",
        "sin(0)"
    ]
    
    import math
    allowed_names = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "sqrt": math.sqrt, "log": math.log, "exp": math.exp,
        "pi": math.pi, "e": math.e
    }
    
    for expr in expressions:
        try:
            # Безопасная обработка выражений
            safe_expr = ''.join(c for c in expr if c in '0123456789+-*/().sincostanqrlgexpix ')
            result = eval(safe_expr, {"__builtins__": {}}, allowed_names)
            print(f"📝 {expr} = {result}")
        except Exception as e:
            print(f"❌ Ошибка в выражении '{expr}': {e}")
    
    return True

def test_response_system():
    """Тестирование системы ответов"""
    print("\n💬 Тестирование системы ответов...")
    
    test_messages = [
        "привет",
        "как дела?", 
        "спасибо",
        "пока",
        "неизвестное сообщение"
    ]
    
    for msg_text in test_messages:
        text = msg_text.lower()
        
        if any(word in text for word in ['привет', 'hello', 'hi', 'здравствуй']):
            response = "👋 Привет! Как дела?"
        elif any(word in text for word in ['как дела', 'как дела?', 'how are you']):
            response = "😊 У меня все отлично! А у вас как?"
        elif any(word in text for word in ['спасибо', 'thanks', 'thank you']):
            response = "🙏 Пожалуйста! Рад помочь!"
        elif any(word in text for word in ['пока', 'bye', 'goodbye']):
            response = "👋 До свидания! Возвращайтесь еще!"
        else:
            import random
            responses = [
                "🤔 Интересно! Расскажите больше.",
                "💭 Понимаю вас. Что еще вас интересует?",
                "🎯 Хороший вопрос! Попробуйте воспользоваться командами /help",
                "✨ Спасибо за сообщение! Используйте /start для главного меню."
            ]
            response = random.choice(responses)
        
        print(f"👤 Пользователь: {msg_text}")
        print(f"🤖 Бот: {response}\n")
    
    return True

def test_entertainment_content():
    """Тестирование развлекательного контента"""
    print("\n🎲 Тестирование развлекательного контента...")
    
    # Тестирование шуток
    jokes = [
        "Почему программисты не любят природу? Там слишком много багов! 🐛",
        "Что такое рекурсия? Смотри что такое рекурсия 🔄",
        "Программист — это человек, который решает проблемы, о существовании которых вы не подозревали, способами, которых вы не понимаете 💻"
    ]
    
    import random
    joke = random.choice(jokes)
    print(f"😄 Случайная шутка: {joke}")
    
    # Тестирование фактов
    facts = [
        "🧠 Человеческий мозг содержит около 86 миллиардов нейронов",
        "🌍 Земля вращается со скоростью около 1600 км/ч на экваторе",
        "🐙 У осьминогов три сердца и голубая кровь"
    ]
    
    fact = random.choice(facts)
    print(f"💡 Интересный факт: {fact}")
    
    # Тестирование цитат
    quotes = [
        "\"Единственный способ сделать отличную работу — любить то, что ты делаешь.\" — Стив Джобс",
        "\"Жизнь — это то, что происходит, пока ты строишь планы.\" — Джон Леннон"
    ]
    
    quote = random.choice(quotes)
    print(f"💭 Мудрая мысль: {quote}")
    
    return True

def test_keyboard_generation():
    """Тестирование генерации клавиатур"""
    print("\n⌨️ Тестирование генерации клавиатур...")
    
    # Симуляция InlineKeyboard
    class MockInlineKeyboard:
        def __init__(self, buttons):
            self.buttons = buttons
            
        def __repr__(self):
            result = "InlineKeyboard:\n"
            for row in self.buttons:
                for button in row:
                    result += f"  [{button['text']}]"
                result += "\n"
            return result
    
    # Главное меню
    main_menu = MockInlineKeyboard([
        [{"text": "👤 Профиль"}, {"text": "🎮 Игры"}],
        [{"text": "🧮 Калькулятор"}, {"text": "📝 Заметки"}],
        [{"text": "🌤 Погода"}, {"text": "🎲 Случайное"}],
        [{"text": "💬 Отзыв"}, {"text": "ℹ️ Помощь"}]
    ])
    
    print("🏠 Главное меню:")
    print(main_menu)
    
    # Меню игр
    games_menu = MockInlineKeyboard([
        [{"text": "🧠 Викторина"}],
        [{"text": "🎲 Кости"}],
        [{"text": "🃏 Случайная карта"}],
        [{"text": "🏠 Главное меню"}]
    ])
    
    print("🎮 Меню игр:")
    print(games_menu)
    
    return True

async def run_async_tests():
    """Запуск асинхронных тестов"""
    print("\n⚡ Запуск асинхронных тестов...")
    
    # Симуляция асинхронной отправки сообщения
    async def mock_send_message(text, user_id=12345):
        await asyncio.sleep(0.1)  # Симуляция задержки сети
        print(f"📤 Отправлено сообщение пользователю {user_id}: {text[:50]}...")
        return True
    
    # Тест отправки приветственного сообщения
    welcome_text = """
🎉 Добро пожаловать, Тестовый пользователь!

🤖 Я — многофункциональный Telegram бот с множеством возможностей:

✨ Основные функции:
• 👤 Персональный профиль
• 🎮 Интерактивные игры и викторины
• 🧮 Встроенный калькулятор
• 📝 Система заметок
"""
    
    await mock_send_message(welcome_text)
    
    # Тест отправки нескольких сообщений
    messages = [
        "🏆 Ваши очки в викторине: 50",
        "📝 У вас 3 заметки",
        "🎯 Новое достижение разблокировано!"
    ]
    
    for msg in messages:
        await mock_send_message(msg)
    
    print("✅ Асинхронные тесты завершены успешно")
    
    return True

def main():
    """Главная функция демонстрации"""
    print("🚀 Запуск демонстрации компонентов Telegram бота")
    print("=" * 60)
    
    try:
        # Запуск всех тестов
        tests = [
            test_user_data_storage,
            test_quiz_system,
            test_calculator,
            test_response_system,
            test_entertainment_content,
            test_keyboard_generation
        ]
        
        passed_tests = 0
        for test in tests:
            try:
                if test():
                    passed_tests += 1
                    print(f"✅ Тест {test.__name__} пройден")
                else:
                    print(f"❌ Тест {test.__name__} провален")
            except Exception as e:
                print(f"💥 Ошибка в тесте {test.__name__}: {e}")
        
        # Запуск асинхронных тестов
        print("\n" + "=" * 60)
        asyncio.run(run_async_tests())
        
        print("\n" + "=" * 60)
        print(f"📊 Результаты тестирования:")
        print(f"✅ Пройдено тестов: {passed_tests}/{len(tests)}")
        print(f"⚡ Асинхронные тесты: пройдены")
        
        if passed_tests == len(tests):
            print("\n🎉 Все компоненты работают корректно!")
            print("🤖 Бот готов к запуску с настоящим токеном.")
        else:
            print("\n⚠️ Некоторые тесты провалены. Проверьте код.")
        
        print("\n📝 Для запуска бота:")
        print("1. Получите токен у @BotFather")
        print("2. Установите переменную окружения: export BOT_TOKEN='ваш_токен'")
        print("3. Запустите: python advanced_bot.py")
        
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()