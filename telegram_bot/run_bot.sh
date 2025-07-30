#!/bin/bash

# Скрипт для запуска Telegram бота
# Использование: ./run_bot.sh [basic|advanced]

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 Telegram Bot Launcher${NC}"
echo "=================================="

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 не найден. Установите Python 3.8+${NC}"
    exit 1
fi

# Проверка зависимостей
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Файл requirements.txt не найден${NC}"
    exit 1
fi

# Установка зависимостей
echo -e "${YELLOW}📦 Проверка зависимостей...${NC}"
pip install -r requirements.txt --quiet

# Проверка токена
if [ -z "$BOT_TOKEN" ]; then
    if [ -f ".env" ]; then
        echo -e "${YELLOW}🔧 Загрузка конфигурации из .env${NC}"
        export $(cat .env | xargs)
    fi
    
    if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "YOUR_BOT_TOKEN_HERE" ]; then
        echo -e "${RED}❌ Токен бота не настроен!${NC}"
        echo -e "${YELLOW}📝 Получите токен у @BotFather в Telegram${NC}"
        echo -e "${YELLOW}🔧 Установите переменную: export BOT_TOKEN='ваш_токен'${NC}"
        echo -e "${YELLOW}📄 Или создайте файл .env на основе .env.example${NC}"
        exit 1
    fi
fi

# Выбор версии бота
VERSION=${1:-advanced}

case $VERSION in
    "basic")
        echo -e "${GREEN}🚀 Запуск базовой версии бота...${NC}"
        python3 main.py
        ;;
    "advanced")
        echo -e "${GREEN}🚀 Запуск расширенной версии бота...${NC}"
        python3 advanced_bot.py
        ;;
    *)
        echo -e "${RED}❌ Неизвестная версия: $VERSION${NC}"
        echo -e "${YELLOW}Использование: ./run_bot.sh [basic|advanced]${NC}"
        exit 1
        ;;
esac