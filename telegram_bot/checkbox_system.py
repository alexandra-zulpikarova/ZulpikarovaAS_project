"""
Система чекбоксов для выбора позиций и ввода количества
Используется для создания заказов, корзины покупок, опросов с множественным выбором
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Состояния для работы с чекбоксами
class CheckboxStates(StatesGroup):
    selecting_items = State()
    entering_quantity = State()
    confirming_order = State()

# Данные товаров/позиций для выбора
AVAILABLE_ITEMS = {
    "pizza_margherita": {
        "name": "🍕 Пицца Маргарита",
        "price": 450,
        "description": "Томатный соус, моцарелла, базилик",
        "category": "pizza"
    },
    "pizza_pepperoni": {
        "name": "🍕 Пицца Пепперони",
        "price": 520,
        "description": "Томатный соус, моцарелла, пепперони",
        "category": "pizza"
    },
    "pizza_quattro": {
        "name": "🍕 Пицца Кватро Формаджи",
        "price": 580,
        "description": "4 сыра: моцарелла, пармезан, горгонзола, рикотта",
        "category": "pizza"
    },
    "burger_classic": {
        "name": "🍔 Классический бургер",
        "price": 320,
        "description": "Говяжья котлета, салат, помидор, огурец",
        "category": "burgers"
    },
    "burger_cheese": {
        "name": "🍔 Чизбургер",
        "price": 380,
        "description": "Говяжья котлета, двойной сыр, салат",
        "category": "burgers"
    },
    "drink_cola": {
        "name": "🥤 Кола",
        "price": 120,
        "description": "Кока-кола 0.5л",
        "category": "drinks"
    },
    "drink_juice": {
        "name": "🧃 Апельсиновый сок",
        "price": 150,
        "description": "Свежевыжатый сок 0.3л",
        "category": "drinks"
    },
    "dessert_tiramisu": {
        "name": "🍰 Тирамису",
        "price": 280,
        "description": "Классический итальянский десерт",
        "category": "desserts"
    },
    "dessert_cheesecake": {
        "name": "🧀 Чизкейк",
        "price": 320,
        "description": "Нежный творожный торт с ягодами",
        "category": "desserts"
    }
}

# Категории для группировки товаров
CATEGORIES = {
    "pizza": "🍕 Пицца",
    "burgers": "🍔 Бургеры", 
    "drinks": "🥤 Напитки",
    "desserts": "🍰 Десерты"
}

class CheckboxManager:
    """Менеджер для работы с чекбоксами и заказами"""
    
    def __init__(self):
        self.user_carts = {}  # Корзины пользователей
    
    def get_user_cart(self, user_id: int) -> Dict:
        """Получить корзину пользователя"""
        if user_id not in self.user_carts:
            self.user_carts[user_id] = {
                "items": {},  # item_id: quantity
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        return self.user_carts[user_id]
    
    def toggle_item(self, user_id: int, item_id: str) -> bool:
        """Переключить выбор товара (добавить/убрать из корзины)"""
        cart = self.get_user_cart(user_id)
        
        if item_id in cart["items"]:
            # Удаляем товар из корзины
            del cart["items"][item_id]
            cart["updated_at"] = datetime.now()
            return False
        else:
            # Добавляем товар в корзину с количеством 1
            cart["items"][item_id] = 1
            cart["updated_at"] = datetime.now()
            return True
    
    def set_item_quantity(self, user_id: int, item_id: str, quantity: int):
        """Установить количество товара"""
        cart = self.get_user_cart(user_id)
        if quantity > 0:
            cart["items"][item_id] = quantity
        elif item_id in cart["items"]:
            del cart["items"][item_id]
        cart["updated_at"] = datetime.now()
    
    def clear_cart(self, user_id: int):
        """Очистить корзину"""
        if user_id in self.user_carts:
            del self.user_carts[user_id]
    
    def calculate_total(self, user_id: int) -> Dict:
        """Рассчитать общую стоимость заказа"""
        cart = self.get_user_cart(user_id)
        total_price = 0
        total_items = 0
        
        for item_id, quantity in cart["items"].items():
            if item_id in AVAILABLE_ITEMS:
                item_price = AVAILABLE_ITEMS[item_id]["price"]
                total_price += item_price * quantity
                total_items += quantity
        
        return {
            "total_price": total_price,
            "total_items": total_items,
            "items_count": len(cart["items"])
        }

# Глобальный менеджер чекбоксов
checkbox_manager = CheckboxManager()

def create_category_keyboard() -> InlineKeyboardMarkup:
    """Создать клавиатуру с категориями товаров"""
    keyboard = []
    
    # Добавляем кнопки категорий
    for category_id, category_name in CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(
            text=category_name,
            callback_data=f"category_{category_id}"
        )])
    
    # Добавляем кнопки управления
    keyboard.extend([
        [InlineKeyboardButton(text="🛒 Моя корзина", callback_data="show_cart")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_items_keyboard(category: str, user_id: int) -> InlineKeyboardMarkup:
    """Создать клавиатуру с товарами категории и чекбоксами"""
    cart = checkbox_manager.get_user_cart(user_id)
    keyboard = []
    
    # Фильтруем товары по категории
    category_items = {k: v for k, v in AVAILABLE_ITEMS.items() if v["category"] == category}
    
    for item_id, item_data in category_items.items():
        # Определяем состояние чекбокса
        is_selected = item_id in cart["items"]
        quantity = cart["items"].get(item_id, 0)
        
        # Эмодзи для чекбокса
        checkbox_emoji = "✅" if is_selected else "☐"
        quantity_text = f" ({quantity})" if is_selected and quantity > 1 else ""
        
        button_text = f"{checkbox_emoji} {item_data['name']}{quantity_text} - {item_data['price']}₽"
        
        keyboard.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"toggle_{item_id}"
        )])
        
        # Если товар выбран, добавляем кнопки изменения количества
        if is_selected:
            qty_buttons = []
            if quantity > 1:
                qty_buttons.append(InlineKeyboardButton(
                    text="➖", callback_data=f"qty_decrease_{item_id}"
                ))
            
            qty_buttons.append(InlineKeyboardButton(
                text=f"Количество: {quantity}", callback_data=f"qty_set_{item_id}"
            ))
            
            qty_buttons.append(InlineKeyboardButton(
                text="➕", callback_data=f"qty_increase_{item_id}"
            ))
            
            keyboard.append(qty_buttons)
    
    # Кнопки навигации
    keyboard.extend([
        [InlineKeyboardButton(text="🔙 К категориям", callback_data="back_to_categories")],
        [InlineKeyboardButton(text="🛒 Моя корзина", callback_data="show_cart")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_cart_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Создать клавиатуру корзины"""
    cart = checkbox_manager.get_user_cart(user_id)
    keyboard = []
    
    if cart["items"]:
        # Кнопки для каждого товара в корзине
        for item_id, quantity in cart["items"].items():
            if item_id in AVAILABLE_ITEMS:
                item_data = AVAILABLE_ITEMS[item_id]
                button_text = f"❌ {item_data['name']} ({quantity})"
                keyboard.append([InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"remove_{item_id}"
                )])
        
        # Кнопки действий
        keyboard.extend([
            [InlineKeyboardButton(text="✅ Оформить заказ", callback_data="confirm_order")],
            [InlineKeyboardButton(text="🗑 Очистить корзину", callback_data="clear_cart")]
        ])
    
    # Навигация
    keyboard.extend([
        [InlineKeyboardButton(text="🔙 Продолжить покупки", callback_data="back_to_categories")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def show_categories_menu(callback: CallbackQuery):
    """Показать меню категорий"""
    text = """
🛍 <b>Добро пожаловать в наш магазин!</b>

Выберите категорию товаров:
"""
    
    keyboard = create_category_keyboard()
    
    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except:
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def show_category_items(callback: CallbackQuery, category: str):
    """Показать товары категории"""
    category_name = CATEGORIES.get(category, "Товары")
    user_id = callback.from_user.id
    
    # Подсчитываем выбранные товары в этой категории
    cart = checkbox_manager.get_user_cart(user_id)
    selected_in_category = sum(1 for item_id in cart["items"] 
                              if item_id in AVAILABLE_ITEMS and 
                              AVAILABLE_ITEMS[item_id]["category"] == category)
    
    text = f"""
{category_name}

Выберите товары (нажмите на товар, чтобы добавить/убрать из корзины):

Выбрано в категории: {selected_in_category}
Всего в корзине: {len(cart["items"])} товаров
"""
    
    keyboard = create_items_keyboard(category, user_id)
    
    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except:
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def show_cart(callback: CallbackQuery):
    """Показать корзину пользователя"""
    user_id = callback.from_user.id
    cart = checkbox_manager.get_user_cart(user_id)
    totals = checkbox_manager.calculate_total(user_id)
    
    if not cart["items"]:
        text = """
🛒 <b>Ваша корзина пуста</b>

Выберите товары из каталога, чтобы добавить их в корзину.
"""
    else:
        text = f"""
🛒 <b>Ваша корзина</b>

<b>Выбранные товары:</b>
"""
        
        for item_id, quantity in cart["items"].items():
            if item_id in AVAILABLE_ITEMS:
                item_data = AVAILABLE_ITEMS[item_id]
                item_total = item_data["price"] * quantity
                text += f"\n• {item_data['name']}\n"
                text += f"  Количество: {quantity} шт.\n"
                text += f"  Цена: {item_data['price']}₽ × {quantity} = {item_total}₽\n"
        
        text += f"""
<b>Итого:</b>
• Товаров: {totals['total_items']} шт.
• Позиций: {totals['items_count']}
• Сумма: {totals['total_price']}₽
"""
    
    keyboard = create_cart_keyboard(user_id)
    
    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except:
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def toggle_item_selection(callback: CallbackQuery, item_id: str):
    """Переключить выбор товара"""
    user_id = callback.from_user.id
    
    if item_id not in AVAILABLE_ITEMS:
        await callback.answer("❌ Товар не найден!")
        return
    
    was_added = checkbox_manager.toggle_item(user_id, item_id)
    item_name = AVAILABLE_ITEMS[item_id]["name"]
    
    if was_added:
        await callback.answer(f"✅ {item_name} добавлен в корзину")
    else:
        await callback.answer(f"❌ {item_name} удален из корзины")
    
    # Обновляем отображение текущей категории
    category = AVAILABLE_ITEMS[item_id]["category"]
    await show_category_items(callback, category)

async def change_item_quantity(callback: CallbackQuery, action: str, item_id: str):
    """Изменить количество товара"""
    user_id = callback.from_user.id
    cart = checkbox_manager.get_user_cart(user_id)
    
    if item_id not in cart["items"]:
        await callback.answer("❌ Товар не найден в корзине!")
        return
    
    current_qty = cart["items"][item_id]
    
    if action == "increase":
        new_qty = min(current_qty + 1, 99)  # Максимум 99 штук
    elif action == "decrease":
        new_qty = max(current_qty - 1, 1)   # Минимум 1 штука
    else:
        return
    
    checkbox_manager.set_item_quantity(user_id, item_id, new_qty)
    
    item_name = AVAILABLE_ITEMS[item_id]["name"]
    await callback.answer(f"🔄 {item_name}: {new_qty} шт.")
    
    # Обновляем отображение
    category = AVAILABLE_ITEMS[item_id]["category"]
    await show_category_items(callback, category)

async def remove_item_from_cart(callback: CallbackQuery, item_id: str):
    """Удалить товар из корзины"""
    user_id = callback.from_user.id
    
    if item_id in AVAILABLE_ITEMS:
        checkbox_manager.toggle_item(user_id, item_id)  # Убираем из корзины
        item_name = AVAILABLE_ITEMS[item_id]["name"]
        await callback.answer(f"🗑 {item_name} удален из корзины")
    
    await show_cart(callback)

async def clear_cart(callback: CallbackQuery):
    """Очистить корзину"""
    user_id = callback.from_user.id
    checkbox_manager.clear_cart(user_id)
    await callback.answer("🗑 Корзина очищена")
    await show_cart(callback)

async def confirm_order(callback: CallbackQuery):
    """Подтвердить заказ"""
    user_id = callback.from_user.id
    cart = checkbox_manager.get_user_cart(user_id)
    totals = checkbox_manager.calculate_total(user_id)
    
    if not cart["items"]:
        await callback.answer("❌ Корзина пуста!")
        return
    
    # Создаем номер заказа
    order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id % 1000:03d}"
    
    # Формируем сообщение о заказе
    order_text = f"""
✅ <b>Заказ #{order_id} оформлен!</b>

<b>Детали заказа:</b>
"""
    
    for item_id, quantity in cart["items"].items():
        if item_id in AVAILABLE_ITEMS:
            item_data = AVAILABLE_ITEMS[item_id]
            item_total = item_data["price"] * quantity
            order_text += f"\n• {item_data['name']}\n"
            order_text += f"  {quantity} шт. × {item_data['price']}₽ = {item_total}₽"
    
    order_text += f"""

<b>Итого:</b>
• Товаров: {totals['total_items']} шт.
• Сумма: {totals['total_price']}₽

<b>Статус:</b> Принят в обработку
<b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}

Спасибо за заказ! Мы свяжемся с вами в ближайшее время.
"""
    
    # Очищаем корзину после оформления
    checkbox_manager.clear_cart(user_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Сделать новый заказ", callback_data="back_to_categories")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(order_text, reply_markup=keyboard, parse_mode="HTML")

# Обработчик всех callback'ов для системы чекбоксов
async def handle_checkbox_callbacks(callback: CallbackQuery, state: FSMContext):
    """Главный обработчик callback'ов для системы чекбоксов"""
    data = callback.data
    
    try:
        if data == "show_shop":
            await show_categories_menu(callback)
        
        elif data.startswith("category_"):
            category = data.replace("category_", "")
            await show_category_items(callback, category)
        
        elif data == "back_to_categories":
            await show_categories_menu(callback)
        
        elif data == "show_cart":
            await show_cart(callback)
        
        elif data.startswith("toggle_"):
            item_id = data.replace("toggle_", "")
            await toggle_item_selection(callback, item_id)
        
        elif data.startswith("qty_increase_"):
            item_id = data.replace("qty_increase_", "")
            await change_item_quantity(callback, "increase", item_id)
        
        elif data.startswith("qty_decrease_"):
            item_id = data.replace("qty_decrease_", "")
            await change_item_quantity(callback, "decrease", item_id)
        
        elif data.startswith("remove_"):
            item_id = data.replace("remove_", "")
            await remove_item_from_cart(callback, item_id)
        
        elif data == "clear_cart":
            await clear_cart(callback)
        
        elif data == "confirm_order":
            await confirm_order(callback)
        
        else:
            await callback.answer("🤷‍♂️ Неизвестная команда")
    
    except Exception as e:
        await callback.answer(f"❌ Произошла ошибка: {str(e)}")
        print(f"Ошибка в handle_checkbox_callbacks: {e}")

# Команда для запуска магазина
async def cmd_shop(message: Message, state: FSMContext):
    """Команда /shop - открыть магазин"""
    text = """
🛍 <b>Добро пожаловать в наш магазин!</b>

Выберите категорию товаров:
"""
    
    keyboard = create_category_keyboard()
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

# Функция для интеграции в основной бот
def setup_checkbox_handlers(dp: Dispatcher):
    """Настройка обработчиков для системы чекбоксов"""
    
    # Команда магазина
    dp.message.register(cmd_shop, lambda message: message.text and message.text.startswith('/shop'))
    
    # Callback обработчики
    dp.callback_query.register(
        handle_checkbox_callbacks,
        lambda callback: any(callback.data.startswith(prefix) for prefix in [
            "show_shop", "category_", "back_to_categories", "show_cart",
            "toggle_", "qty_", "remove_", "clear_cart", "confirm_order"
        ])
    )