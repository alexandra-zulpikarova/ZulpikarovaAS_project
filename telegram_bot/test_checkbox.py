#!/usr/bin/env python3
"""
Тест системы чекбоксов
Демонстрирует работу с выбором позиций и количества
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from checkbox_system import CheckboxManager, AVAILABLE_ITEMS, CATEGORIES

def test_checkbox_manager():
    """Тестирование основной функциональности CheckboxManager"""
    print("🧪 Тестирование CheckboxManager...")
    
    manager = CheckboxManager()
    test_user_id = 12345
    
    # Тест 1: Создание корзины
    print("\n1️⃣ Создание корзины пользователя")
    cart = manager.get_user_cart(test_user_id)
    print(f"✅ Корзина создана: {cart}")
    
    # Тест 2: Добавление товаров
    print("\n2️⃣ Добавление товаров в корзину")
    items_to_add = ["pizza_margherita", "burger_classic", "drink_cola"]
    
    for item_id in items_to_add:
        was_added = manager.toggle_item(test_user_id, item_id)
        item_name = AVAILABLE_ITEMS[item_id]["name"]
        print(f"{'✅' if was_added else '❌'} {item_name} {'добавлен' if was_added else 'удален'}")
    
    # Тест 3: Изменение количества
    print("\n3️⃣ Изменение количества товаров")
    manager.set_item_quantity(test_user_id, "pizza_margherita", 2)
    manager.set_item_quantity(test_user_id, "drink_cola", 3)
    
    cart = manager.get_user_cart(test_user_id)
    for item_id, quantity in cart["items"].items():
        item_name = AVAILABLE_ITEMS[item_id]["name"]
        print(f"📦 {item_name}: {quantity} шт.")
    
    # Тест 4: Расчет общей стоимости
    print("\n4️⃣ Расчет общей стоимости")
    totals = manager.calculate_total(test_user_id)
    print(f"💰 Общая стоимость: {totals['total_price']}₽")
    print(f"📦 Общее количество товаров: {totals['total_items']} шт.")
    print(f"🛒 Позиций в корзине: {totals['items_count']}")
    
    # Тест 5: Удаление товара
    print("\n5️⃣ Удаление товара из корзины")
    manager.toggle_item(test_user_id, "burger_classic")
    print("🗑 Бургер удален из корзины")
    
    # Финальное состояние корзины
    print("\n📊 Финальное состояние корзины:")
    cart = manager.get_user_cart(test_user_id)
    totals = manager.calculate_total(test_user_id)
    
    for item_id, quantity in cart["items"].items():
        item_data = AVAILABLE_ITEMS[item_id]
        item_total = item_data["price"] * quantity
        print(f"• {item_data['name']}: {quantity} шт. × {item_data['price']}₽ = {item_total}₽")
    
    print(f"\n💸 Итого к оплате: {totals['total_price']}₽")
    
    # Тест 6: Очистка корзины
    print("\n6️⃣ Очистка корзины")
    manager.clear_cart(test_user_id)
    cart = manager.get_user_cart(test_user_id)
    print(f"🗑 Корзина очищена. Товаров в корзине: {len(cart['items'])}")
    
    return True

def test_item_categories():
    """Тестирование категорий товаров"""
    print("\n🏷 Тестирование категорий товаров...")
    
    for category_id, category_name in CATEGORIES.items():
        print(f"\n📂 {category_name}:")
        
        # Находим товары этой категории
        category_items = {k: v for k, v in AVAILABLE_ITEMS.items() if v["category"] == category_id}
        
        for item_id, item_data in category_items.items():
            print(f"  • {item_data['name']} - {item_data['price']}₽")
            print(f"    {item_data['description']}")
    
    print(f"\n📊 Всего категорий: {len(CATEGORIES)}")
    print(f"📦 Всего товаров: {len(AVAILABLE_ITEMS)}")
    
    return True

def test_multiple_users():
    """Тестирование работы с несколькими пользователями"""
    print("\n👥 Тестирование нескольких пользователей...")
    
    manager = CheckboxManager()
    users = [11111, 22222, 33333]
    
    # Каждый пользователь добавляет разные товары
    user_items = {
        11111: ["pizza_margherita", "drink_cola"],
        22222: ["burger_classic", "dessert_tiramisu"],
        33333: ["pizza_pepperoni", "drink_juice", "dessert_cheesecake"]
    }
    
    for user_id, items in user_items.items():
        print(f"\n👤 Пользователь {user_id}:")
        
        for item_id in items:
            manager.toggle_item(user_id, item_id)
            item_name = AVAILABLE_ITEMS[item_id]["name"]
            print(f"  ✅ Добавил: {item_name}")
        
        # Устанавливаем разное количество
        if len(items) > 0:
            manager.set_item_quantity(user_id, items[0], 2)
            print(f"  🔢 Количество {AVAILABLE_ITEMS[items[0]]['name']}: 2 шт.")
        
        # Показываем итоги
        totals = manager.calculate_total(user_id)
        print(f"  💰 Итого: {totals['total_price']}₽ ({totals['total_items']} товаров)")
    
    return True

def simulate_checkbox_ui():
    """Симуляция пользовательского интерфейса с чекбоксами"""
    print("\n🖥 Симуляция UI с чекбоксами...")
    
    manager = CheckboxManager()
    user_id = 99999
    
    print("🛍 Добро пожаловать в магазин!")
    print("Выберите категорию:")
    
    for i, (category_id, category_name) in enumerate(CATEGORIES.items(), 1):
        print(f"  {i}. {category_name}")
    
    # Симулируем выбор категории "pizza"
    selected_category = "pizza"
    category_name = CATEGORIES[selected_category]
    print(f"\n📂 Выбрана категория: {category_name}")
    
    # Показываем товары с чекбоксами
    cart = manager.get_user_cart(user_id)
    category_items = {k: v for k, v in AVAILABLE_ITEMS.items() if v["category"] == selected_category}
    
    print("\nТовары (☐ - не выбран, ✅ - выбран):")
    for item_id, item_data in category_items.items():
        is_selected = item_id in cart["items"]
        quantity = cart["items"].get(item_id, 0)
        checkbox = "✅" if is_selected else "☐"
        quantity_text = f" ({quantity})" if is_selected and quantity > 1 else ""
        
        print(f"  {checkbox} {item_data['name']}{quantity_text} - {item_data['price']}₽")
    
    # Симулируем выбор товаров
    print("\n🖱 Симулируем выбор товаров...")
    
    # Добавляем пиццу Маргарита
    manager.toggle_item(user_id, "pizza_margherita")
    print("✅ Добавлена: Пицца Маргарита")
    
    # Добавляем пиццу Пепперони
    manager.toggle_item(user_id, "pizza_pepperoni")
    print("✅ Добавлена: Пицца Пепперони")
    
    # Увеличиваем количество Маргариты
    manager.set_item_quantity(user_id, "pizza_margherita", 2)
    print("🔢 Пицца Маргарита: количество изменено на 2")
    
    # Показываем обновленный список
    print("\n📋 Обновленный список:")
    cart = manager.get_user_cart(user_id)
    
    for item_id, item_data in category_items.items():
        is_selected = item_id in cart["items"]
        quantity = cart["items"].get(item_id, 0)
        checkbox = "✅" if is_selected else "☐"
        quantity_text = f" ({quantity})" if is_selected and quantity > 1 else ""
        
        print(f"  {checkbox} {item_data['name']}{quantity_text} - {item_data['price']}₽")
    
    # Показываем корзину
    print("\n🛒 Содержимое корзины:")
    totals = manager.calculate_total(user_id)
    
    for item_id, quantity in cart["items"].items():
        item_data = AVAILABLE_ITEMS[item_id]
        item_total = item_data["price"] * quantity
        print(f"  • {item_data['name']}: {quantity} шт. × {item_data['price']}₽ = {item_total}₽")
    
    print(f"\n💸 Итого: {totals['total_price']}₽ ({totals['total_items']} товаров)")
    
    return True

def main():
    """Главная функция тестирования"""
    print("🧪 Запуск тестов системы чекбоксов")
    print("=" * 50)
    
    tests = [
        test_checkbox_manager,
        test_item_categories,
        test_multiple_users,
        simulate_checkbox_ui
    ]
    
    passed_tests = 0
    
    for test_func in tests:
        try:
            print(f"\n▶️ Запуск теста: {test_func.__name__}")
            if test_func():
                passed_tests += 1
                print(f"✅ Тест {test_func.__name__} пройден")
            else:
                print(f"❌ Тест {test_func.__name__} провален")
        except Exception as e:
            print(f"💥 Ошибка в тесте {test_func.__name__}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Результаты тестирования:")
    print(f"✅ Пройдено: {passed_tests}/{len(tests)} тестов")
    
    if passed_tests == len(tests):
        print("\n🎉 Все тесты пройдены успешно!")
        print("🤖 Система чекбоксов готова к использованию в боте.")
        print("\n📝 Для запуска бота с магазином:")
        print("1. Убедитесь, что файл checkbox_system.py находится в той же папке")
        print("2. Запустите: python advanced_bot.py")
        print("3. В боте используйте команду /shop или кнопку 🛍 Магазин")
    else:
        print("\n⚠️ Некоторые тесты провалены. Проверьте код.")
    
    return passed_tests == len(tests)

if __name__ == "__main__":
    main()