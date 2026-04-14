# ⚡ Швидкий старт

## Крок за кроком запуск за 5 хвилин

### 1️⃣ Встановіть Python 3.10+ та створіть віртуальне середовище

```bash
# Створіть віртуальне середовище
python -m venv venv

# Активуйте його
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2️⃣ Встановіть залежності

```bash
pip install -r requirements.txt
```

### 3️⃣ Отримайте API ключі

**Telegram Bot Token:**
1. Відкрийте [@BotFather](https://t.me/BotFather) в Telegram
2. Надішліть `/newbot`
3. Дотримуйтесь інструкцій та скопіюйте токен

**OpenAI API Key:**
1. Зареєструйтесь на [platform.openai.com](https://platform.openai.com)
2. Створіть API ключ в розділі "API Keys"
3. Скопіюйте ключ

### 4️⃣ Створіть файл `.env`

Створіть файл `.env` в папці `project/` з таким вмістом:

```env
BOT_TOKEN=ваш_токен_від_BotFather
OPENAI_API_KEY=ваш_ключ_від_OpenAI
DATABASE_PATH=career_twin.db
OPENAI_MODEL=gpt-4o-mini
```

### 5️⃣ Запустіть бота

```bash
python main.py
```

### 6️⃣ Протестуйте

1. Знайдіть вашого бота в Telegram
2. Надішліть `/start`
3. Почніть тестування!

---

📖 **Детальні інструкції:** дивіться [README_IMPLEMENTATION.md](README_IMPLEMENTATION.md)

