#!/bin/bash
echo "==================================="
echo "Запуск Career-TwinNavigatorBot"
echo "==================================="
echo ""

if [ ! -d "venv" ]; then
    echo "ПОМИЛКА: Віртуальне середовище не знайдено!"
    echo "Запустіть спочатку: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "ПОМИЛКА: Файл .env не знайдено!"
    echo "Створіть .env на основі env.example"
    exit 1
fi

echo "Активація віртуального середовища..."
source venv/bin/activate

echo ""
echo "Запуск бота..."
python main.py

