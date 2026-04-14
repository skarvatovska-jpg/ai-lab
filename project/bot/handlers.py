"""
Обробники повідомлень та команд для бота
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from database import Database
from ai_engine.behavior_analyzer import BehaviorAnalyzer
from ai_engine.scenario_generator import ScenarioGenerator
from ai_engine.burnout_predictor import BurnoutPredictor
from bot.states import SurveyStates, SimulationStates

router = Router()

# Ініціалізація компонентів
db = Database()
behavior_analyzer = BehaviorAnalyzer()
scenario_generator = ScenarioGenerator()
burnout_predictor = BurnoutPredictor()

# Головне меню з кнопками "Почати" та "Завершити"
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="▶️ Почати"),
            KeyboardButton(text="⏹ Завершити")
        ]
    ],
    resize_keyboard=True
)

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обробник команди /start"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Додаємо користувача до БД
    await db.add_user(user_id, username, first_name)
    
    # Привітання
    welcome_text = (
        "👋 Привіт! Я — **Career-TwinNavigator**.\n\n"
        "Створю твого цифрового двійника і перевірю тебе у реальних професійних "
        "сценаріях, щоб спрогнозувати ризик вигорання.\n\n"
        "Почнемо аналіз! 🔍"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Почати аналіз", callback_data="start_survey")],
        [InlineKeyboardButton(text="ℹ️ Про мене", callback_data="about")]
    ])
    
    await message.answer("Оберіть дію:", reply_markup=main_menu_kb)
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")
    await state.clear()

@router.message(F.text == "▶️ Почати")
async def btn_start_handler(message: Message, state: FSMContext):
    """Обробник кнопки 'Почати'"""
    await cmd_start(message, state)

@router.message(F.text == "⏹ Завершити")
async def btn_finish_handler(message: Message, state: FSMContext):
    """Обробник кнопки 'Завершити'"""
    await state.clear()
    await message.answer(
        "🛑 Роботу завершено. Усі поточні процеси зупинено.\n\n"
        "Натисніть «▶️ Почати», щоб розпочати знову.", 
        reply_markup=main_menu_kb
    )


@router.callback_query(F.data == "about")
async def about_bot(callback: CallbackQuery):
    """Інформація про бота"""
    about_text = (
        "ℹ️ **Career-TwinNavigator**\n\n"
        "Інноваційний Telegram-бот для вибору кар'єри на основі:\n"
        "• Поведінкового аналізу (аналог Big5)\n"
        "• Рольових симуляцій професійних сценаріїв\n"
        "• Прогнозу ризику вигорання (Burnout)\n"
        "• Персоналізованих рекомендацій\n\n"
        "Замість тестів на навички, я аналізую як ти *реагуєш* на стрес, хаос та рутину."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Почати аналіз", callback_data="start_survey")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start")]
    ])
    
    await callback.message.edit_text(about_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "start_survey")
async def start_survey(callback: CallbackQuery, state: FSMContext):
    """Початок анкети"""
    await callback.answer()
    
    text = (
        "📋 **Анкета цифрового двійника**\n\n"
        "Дай відповіді на 10 коротких питань.\n\n"
        "**1/10. Хаос vs Рутина**\n"
        "Що ближче, якщо день ламає всі плани?"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Це навіть заряджає, люблю хаос", callback_data="survey_chaos")],
        [InlineKeyboardButton(text="🔄 Ненавиджу, люблю чіткий план", callback_data="survey_routine")],
        [InlineKeyboardButton(text="⚖️ Ок, якщо є базова структура", callback_data="survey_balance")],
        [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="survey_custom")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SurveyStates.waiting_chaos_routine)


@router.callback_query(F.data.in_(["survey_chaos", "survey_routine", "survey_balance", "survey_custom"]), SurveyStates.waiting_chaos_routine)
async def process_chaos_routine(callback: CallbackQuery, state: FSMContext):
    """Обробка відповіді на питання про хаос/рутину"""
    if callback.data == "survey_chaos":
        answer = "chaos"
    elif callback.data == "survey_routine":
        answer = "routine"
    elif callback.data == "survey_balance":
        answer = "balance"
    else:
        # Обробка натискання "Своя відповідь"
        await callback.message.answer("✏️ Твоя відповідь (кілька слів):")
        await callback.answer()
        await state.set_state(SurveyStates.waiting_q1_custom)
        return

    await state.update_data(chaos_vs_routine=answer)
    
    text = (
        "**2/10. Дедлайни та свобода**\n\n"
        "Уяви задачу на кілька днів. Як тобі комфортніше працювати з нею?"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Все розписано по кроках і термінах", callback_data="survey_planned")],
        [InlineKeyboardButton(text="🎲 Є лише приблизний дедлайн, роблю як відчуваю", callback_data="survey_freedom")],
        [InlineKeyboardButton(text="🔁 Мені потрібна рамка, але без мікроконтролю", callback_data="survey_flex")],
        [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="survey_custom")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
    await state.set_state(SurveyStates.waiting_deadline)


@router.callback_query(F.data.in_(["survey_planned", "survey_freedom", "survey_flex", "survey_custom"]), SurveyStates.waiting_deadline)
async def process_deadline(callback: CallbackQuery, state: FSMContext):
    """Обробка відповіді на питання про дедлайни"""
    if callback.data == "survey_planned":
        answer = "planned"
    elif callback.data == "survey_freedom":
        answer = "freedom"
    elif callback.data == "survey_flex":
        answer = "flex"
    else:
        # Обробка натискання "Своя відповідь"
        await callback.message.answer("✏️ Твоя відповідь (кілька слів):")
        await callback.answer()
        await state.set_state(SurveyStates.waiting_q2_custom)
        return

    await state.update_data(deadline_reaction=answer)
    
    text = (
        "**3/10. Емоційний тригер**\n\n"
        "Що найбільше виснажує тебе на роботі/навчанні? (наприклад: дедлайни, тиск)."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
    await state.set_state(SurveyStates.waiting_emotional_trigger)


@router.message(SurveyStates.waiting_emotional_trigger)
async def process_emotional_trigger(message: Message, state: FSMContext):
    """Обробка відповіді про емоційний тригер"""
    emotional_trigger = message.text
    await state.update_data(emotional_trigger=emotional_trigger)
    
    text = (
        "**4/10. Реакція в конфлікті**\n\n"
        "Колега/клієнт публічно незадоволений твоєю роботою. Твої дії?"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤝 Спочатку слухаю, намагаюсь зрозуміти й знайти компроміс", callback_data="survey_compromise")],
        [InlineKeyboardButton(text="⚖️ Чітко відстоюю свою позицію, навіть якщо це загострює розмову", callback_data="survey_assertive")],
        [InlineKeyboardButton(text="😔 Максимально згладжую, уникаю конфронтації", callback_data="survey_avoid")],
        [InlineKeyboardButton(text="🧊 Беру паузу, щоб охолонути, і повертаюся до розмови пізніше", callback_data="survey_pause")],
        [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="survey_custom")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SurveyStates.waiting_conflict)


@router.callback_query(
    F.data.in_(["survey_compromise", "survey_assertive", "survey_avoid", "survey_pause", "survey_custom"]),
    SurveyStates.waiting_conflict,
)
async def process_conflict(callback: CallbackQuery, state: FSMContext):
    """Обробка відповіді про конфлікт та перехід до наступних питань"""
    if callback.data == "survey_custom":
        await callback.message.answer("✏️ Твоя відповідь (кілька слів):")
        await callback.answer()
        await state.set_state(SurveyStates.waiting_q4_custom)
        return

    conflict_map = {
        "survey_compromise": "компроміс",
        "survey_assertive": "відстоювання позиції",
        "survey_avoid": "уникнення",
        "survey_pause": "беру паузу перед розмовою"
    }
    conflict_reaction = conflict_map.get(callback.data, "компроміс")
    await state.update_data(conflict_reaction=conflict_reaction)

    # Питання 5: енергія після дня спілкування
    text = (
        "**5/10. Після повного дня спілкування**\n\n"
        "Як ти почуваєшся після дня, коли було багато зустрічей, дзвінків і взаємодії з людьми?"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔋 Відчуваю заряд енергії", callback_data="q5_charged")],
            [InlineKeyboardButton(text="🔌 Вимотаний(а), хочу тиші і усамітнення", callback_data="q5_drained")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q5_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ]
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
    await state.set_state(SurveyStates.waiting_q5)


@router.callback_query(
    F.data.in_(["q5_charged", "q5_drained", "q5_custom"]),
    SurveyStates.waiting_q5,
)
async def process_q5(callback: CallbackQuery, state: FSMContext):
    """Питання 6: командна робота vs самостійність"""
    if callback.data == "q5_custom":
        await callback.message.answer("✏️ Твоя відповідь (кілька слів):")
        await callback.answer()
        await state.set_state(SurveyStates.waiting_q5_custom)
        return

    await state.update_data(social_energy="charged" if callback.data == "q5_charged" else "drained")

    text = (
        "**6/10. Команда чи соло**\n\n"
        "Уяви, що тобі дають складну задачу. Як тобі комфортніше її вирішувати?"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 В команді, з обговореннями та брейнштормами", callback_data="q6_team")],
            [InlineKeyboardButton(text="👤 Наодинці, у своєму ритмі", callback_data="q6_solo")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q6_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ]
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
    await state.set_state(SurveyStates.waiting_q6)


@router.callback_query(
    F.data.in_(["q6_team", "q6_solo", "q6_custom"]),
    SurveyStates.waiting_q6,
)
async def process_q6(callback: CallbackQuery, state: FSMContext):
    """Питання 7: ставлення до рутини"""
    if callback.data == "q6_custom":
        await callback.message.answer("✏️ Твоя відповідь (кілька слів):")
        await callback.answer()
        await state.set_state(SurveyStates.waiting_q6_custom)
        return

    await state.update_data(team_vs_solo="team" if callback.data == "q6_team" else "solo")

    text = (
        "**7/10. Рутинні задачі**\n\n"
        "Як ти ставишся до задач, де потрібно багато разів повторювати одну й ту саму дію?"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="😌 Це ок, навіть заспокоює", callback_data="q7_ok")],
            [InlineKeyboardButton(text="😵 Дуже швидко втомлююсь і відволікаюсь", callback_data="q7_tired")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q7_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ]
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
    await state.set_state(SurveyStates.waiting_q7)


@router.callback_query(
    F.data.in_(["q7_ok", "q7_tired", "q7_custom"]),
    SurveyStates.waiting_q7,
)
async def process_q7(callback: CallbackQuery, state: FSMContext):
    """Питання 8: ризик та нові можливості"""
    if callback.data == "q7_custom":
        await callback.message.answer("✏️ Твоя відповідь (кілька слів):")
        await callback.answer()
        await state.set_state(SurveyStates.waiting_q7_custom)
        return

    await state.update_data(monotony_reaction="ok" if callback.data == "q7_ok" else "tired")

    text = (
        "**8/10. Нові можливості та ризик**\n\n"
        "Тобі пропонують ризиковий проєкт з великим потенціалом. Як реагуєш?"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔥 Берусь, навіть якщо страшно", callback_data="q8_risk")],
            [InlineKeyboardButton(text="🤔 Спочатку хочу більше інформації і гарантій", callback_data="q8_careful")],
            [InlineKeyboardButton(text="🧱 Краще стабільність, ніж ризик", callback_data="q8_stable")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q8_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ]
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
    await state.set_state(SurveyStates.waiting_q8)


@router.callback_query(
    F.data.in_(["q8_risk", "q8_careful", "q8_stable", "q8_custom"]),
    SurveyStates.waiting_q8,
)
async def process_q8(callback: CallbackQuery, state: FSMContext):
    """Питання 9: як ти навчаєшся"""
    if callback.data == "q8_custom":
        await callback.message.answer("✏️ Твоя відповідь (кілька слів):")
        await callback.answer()
        await state.set_state(SurveyStates.waiting_q8_custom)
        return

    mapping = {
        "q8_risk": "risk",
        "q8_careful": "careful",
        "q8_stable": "stable",
    }
    await state.update_data(risk_style=mapping.get(callback.data, "careful"))

    text = (
        "**9/10. Стиль навчання**\n\n"
        "Як ти зазвичай вивчаєш щось нове?"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 Читаю інструкції, статті, дивлюсь курси", callback_data="q9_theory")],
            [InlineKeyboardButton(text="🧪 Одразу пробую на практиці і вчуся по ходу", callback_data="q9_practice")],
            [InlineKeyboardButton(text="🙋‍♂️ Питаю в людей, яким довіряю", callback_data="q9_people")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q9_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ]
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
    await state.set_state(SurveyStates.waiting_q9)


@router.callback_query(
    F.data.in_(["q9_theory", "q9_practice", "q9_people", "q9_custom"]),
    SurveyStates.waiting_q9,
)
async def process_q9(callback: CallbackQuery, state: FSMContext):
    """Питання 10: образ бажаного майбутнього (вільний текст)"""
    if callback.data == "q9_custom":
        await callback.message.answer("✏️ Твоя відповідь (кілька слів):")
        await callback.answer()
        await state.set_state(SurveyStates.waiting_q9_custom)
        return

    mapping = {
        "q9_theory": "theory_first",
        "q9_practice": "practice_first",
        "q9_people": "people_first",
    }
    await state.update_data(learning_style=mapping.get(callback.data, "practice_first"))

    text = (
        "**10/10. Ідеальний день**\n\n"
        "Опиши свій ідеальний робочий день за 3-5 років (одне речення)."
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
    await state.set_state(SurveyStates.waiting_q10)


@router.message(SurveyStates.waiting_q10)
async def finish_survey_and_analyze(message: Message, state: FSMContext):
    """Завершення анкети з 10 питань та запуск аналізу"""
    await state.update_data(ideal_day=message.text.strip())
    await _finalize_survey(message, state)


# --- Custom Answer Handlers ---

@router.message(SurveyStates.waiting_q1_custom)
async def process_q1_custom_msg(message: Message, state: FSMContext):
    await state.update_data(chaos_vs_routine=message.text)
    
    text = (
        "**2/10. Дедлайни та свобода**\n\n"
        "Як тобі комфортніше працювати з довгою задачею?"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Все розписано по кроках і термінах", callback_data="survey_planned")],
        [InlineKeyboardButton(text="🎲 Є лише приблизний дедлайн, роблю як відчуваю", callback_data="survey_freedom")],
        [InlineKeyboardButton(text="🔁 Мені потрібна рамка, але без мікроконтролю", callback_data="survey_flex")],
        [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="survey_custom")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
    ])
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SurveyStates.waiting_deadline)


@router.message(SurveyStates.waiting_q2_custom)
async def process_q2_custom_msg(message: Message, state: FSMContext):
    await state.update_data(deadline_reaction=message.text)
    
    text = (
        "**3/10. Емоційний тригер**\n\n"
        "Що найбільше виснажує тебе на роботі? (дедлайни, тиск, хаос)."
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]])
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SurveyStates.waiting_emotional_trigger)


@router.message(SurveyStates.waiting_q4_custom)
async def process_q4_custom_msg(message: Message, state: FSMContext):
    await state.update_data(conflict_reaction=message.text)
    
    # Питання 5: енергія після дня спілкування
    text = (
        "**5/10. Після дня спілкування**\n\n"
        "Як почуваєшся після десятка робочих зустрічей та дзвінків?"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔋 Відчуваю заряд енергії", callback_data="q5_charged")],
            [InlineKeyboardButton(text="🔌 Вимотаний(а), хочу тиші і усамітнення", callback_data="q5_drained")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q5_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ]
    )
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SurveyStates.waiting_q5)


@router.message(SurveyStates.waiting_q5_custom)
async def process_q5_custom_msg(message: Message, state: FSMContext):
    await state.update_data(social_energy=message.text)
    
    text = (
        "**6/10. Команда чи соло**\n\n"
        "Як тобі комфортніше вирішувати складну задачу?"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 В команді, з обговореннями та брейнштормами", callback_data="q6_team")],
            [InlineKeyboardButton(text="👤 Наодинці, у своєму ритмі", callback_data="q6_solo")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q6_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ]
    )
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SurveyStates.waiting_q6)


@router.message(SurveyStates.waiting_q6_custom)
async def process_q6_custom_msg(message: Message, state: FSMContext):
    await state.update_data(team_vs_solo=message.text)
    
    text = (
        "**7/10. Рутинні задачі**\n\n"
        "Як ти ставишся до задач, де потрібно багато разів повторювати одну й ту саму дію?"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="😌 Це ок, навіть заспокоює", callback_data="q7_ok")],
            [InlineKeyboardButton(text="😵 Дуже швидко втомлююсь і відволікаюсь", callback_data="q7_tired")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q7_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ]
    )
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SurveyStates.waiting_q7)


@router.message(SurveyStates.waiting_q7_custom)
async def process_q7_custom_msg(message: Message, state: FSMContext):
    await state.update_data(monotony_reaction=message.text)
    
    text = (
        "**8/10. Нові можливості та ризик**\n\n"
        "Тобі пропонують ризиковий проєкт з великим потенціалом. Як реагуєш?"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔥 Берусь, навіть якщо страшно", callback_data="q8_risk")],
            [InlineKeyboardButton(text="🤔 Спочатку хочу більше інформації і гарантій", callback_data="q8_careful")],
            [InlineKeyboardButton(text="🧱 Краще стабільність, ніж ризик", callback_data="q8_stable")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q8_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ]
    )
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SurveyStates.waiting_q8)


@router.message(SurveyStates.waiting_q8_custom)
async def process_q8_custom_msg(message: Message, state: FSMContext):
    await state.update_data(risk_style=message.text)
    
    text = (
        "**9/10. Стиль навчання**\n\n"
        "Як ти зазвичай вивчаєш щось нове?"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 Читаю інструкції, статті, дивлюсь курси", callback_data="q9_theory")],
            [InlineKeyboardButton(text="🧪 Одразу пробую на практиці і вчуся по ходу", callback_data="q9_practice")],
            [InlineKeyboardButton(text="🙋‍♂️ Питаю в людей, яким довіряю", callback_data="q9_people")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q9_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ]
    )
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SurveyStates.waiting_q9)


@router.message(SurveyStates.waiting_q9_custom)
async def process_q9_custom_msg(message: Message, state: FSMContext):
    await state.update_data(learning_style=message.text)
    
    text = (
        "**10/10. Образ твого «ідеального дня»**\n\n"
        "Опиши кількома словами або 1–2 короткими реченнями, "
        "яким ти бачиш свій ідеальний робочий день через кілька років."
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]])
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SurveyStates.waiting_q10)




@router.callback_query(F.data == "survey_back")
async def process_survey_back(callback: CallbackQuery, state: FSMContext):
    current = await state.get_state()
    
    if current in (SurveyStates.waiting_deadline.state, SurveyStates.waiting_q1_custom.state):
        await start_survey(callback, state)
        
    elif current in (SurveyStates.waiting_emotional_trigger.state, SurveyStates.waiting_q2_custom.state):
        text = "**2/10. Дедлайни та свобода**\n\nУяви задачу на кілька днів. Як тобі комфортніше працювати з нею?"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Все розписано по кроках і термінах", callback_data="survey_planned")],
            [InlineKeyboardButton(text="🎲 Є лише приблизний дедлайн, роблю як відчуваю", callback_data="survey_freedom")],
            [InlineKeyboardButton(text="🔁 Мені потрібна рамка, але без мікроконтролю", callback_data="survey_flex")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="survey_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(SurveyStates.waiting_deadline)
        
    elif current in (SurveyStates.waiting_conflict.state, SurveyStates.waiting_q4_custom.state):
        text = "**3/10. Емоційний тригер**\n\nЩо найбільше виснажує тебе на роботі/навчанні? (наприклад: дедлайни, тиск)."
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(SurveyStates.waiting_emotional_trigger)
        
    elif current in (SurveyStates.waiting_q5.state, SurveyStates.waiting_q5_custom.state):
        text = "**4/10. Реакція в конфлікті**\n\nКолега/клієнт публічно незадоволений твоєю роботою. Твої дії?"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🤝 Спочатку слухаю, намагаюсь зрозуміти й знайти компроміс", callback_data="survey_compromise")],
            [InlineKeyboardButton(text="⚖️ Чітко відстоюю свою позицію, навіть якщо це загострює розмову", callback_data="survey_assertive")],
            [InlineKeyboardButton(text="😔 Максимально згладжую, уникаю конфронтації", callback_data="survey_avoid")],
            [InlineKeyboardButton(text="🧊 Беру паузу, щоб охолонути, і повертаюся до розмови пізніше", callback_data="survey_pause")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="survey_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(SurveyStates.waiting_conflict)
        
    elif current in (SurveyStates.waiting_q6.state, SurveyStates.waiting_q6_custom.state):
        text = "**5/10. Після повного дня спілкування**\n\nЯк ти почуваєшся після дня, коли було багато зустрічей, дзвінків і взаємодії з людьми?"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔋 Відчуваю заряд енергії", callback_data="q5_charged")],
            [InlineKeyboardButton(text="🔌 Вимотаний(а), хочу тиші і усамітнення", callback_data="q5_drained")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q5_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(SurveyStates.waiting_q5)
        
    elif current in (SurveyStates.waiting_q7.state, SurveyStates.waiting_q7_custom.state):
        text = "**6/10. Команда чи соло**\n\nУяви, що тобі дають складну задачу. Як тобі комфортніше її вирішувати?"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 В команді, з обговореннями та брейнштормами", callback_data="q6_team")],
            [InlineKeyboardButton(text="👤 Наодинці, у своєму ритмі", callback_data="q6_solo")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q6_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(SurveyStates.waiting_q6)
        
    elif current in (SurveyStates.waiting_q8.state, SurveyStates.waiting_q8_custom.state):
        text = "**7/10. Рутинні задачі**\n\nЯк ти ставишся до задач, де потрібно багато разів повторювати одну й ту саму дію?"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="😌 Це ок, навіть заспокоює", callback_data="q7_ok")],
            [InlineKeyboardButton(text="😵 Дуже швидко втомлююсь і відволікаюсь", callback_data="q7_tired")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q7_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(SurveyStates.waiting_q7)
        
    elif current in (SurveyStates.waiting_q9.state, SurveyStates.waiting_q9_custom.state):
        text = "**8/10. Нові можливості та ризик**\n\nТобі пропонують ризиковий проєкт з великим потенціалом. Як реагуєш?"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔥 Берусь, навіть якщо страшно", callback_data="q8_risk")],
            [InlineKeyboardButton(text="🤔 Спочатку хочу більше інформації і гарантій", callback_data="q8_careful")],
            [InlineKeyboardButton(text="🧱 Краще стабільність, ніж ризик", callback_data="q8_stable")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q8_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(SurveyStates.waiting_q8)
        
    elif current in (SurveyStates.waiting_q10.state,):
        text = "**9/10. Стиль навчання**\n\nЯк ти зазвичай вивчаєш щось нове?"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 Читаю інструкції, статті, дивлюсь курси", callback_data="q9_theory")],
            [InlineKeyboardButton(text="🧪 Одразу пробую на практиці і вчуся по ходу", callback_data="q9_practice")],
            [InlineKeyboardButton(text="🙋‍♂️ Питаю в людей, яким довіряю", callback_data="q9_people")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q9_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(SurveyStates.waiting_q9)
        
    else:
        await callback.answer("Немає куди повертатись", show_alert=True)

async def _finalize_survey(message: Message, state: FSMContext):
    """Спільна функція завершення опитування"""
    data = await state.get_data()

    # Мапінг відповідей для аналізу (для кнопок)
    # Якщо там кастомний текст - він залишиться текстом, це ок.
    chaos_val = data.get("chaos_vs_routine")
    if chaos_val == "chaos": chaos_text = "люблю хаос"
    elif chaos_val == "routine": chaos_text = "люблю рутину"
    elif chaos_val == "balance": chaos_text = "баланс"
    else: chaos_text = chaos_val # custom

    deadline_val = data.get("deadline_reaction")
    if deadline_val == "planned": deadline_text = "план"
    elif deadline_val == "freedom": deadline_text = "свобода"
    elif deadline_val == "flex": deadline_text = "гнучкість"
    else: deadline_text = deadline_val # custom

    # ... інші поля теж можуть бути текстом ...
    def map_val(val, mapping, default):
        if val in mapping: return mapping[val]
        return val # Custom text

    # Q5 Social Energy
    social_map = {"charged": "заряджає", "drained": "вимотує"}
    social_text = map_val(data.get("social_energy"), social_map, "не вказано")

    # Q6 Team vs Solo
    team_map = {"team": "команда", "solo": "соло"}
    team_text = map_val(data.get("team_vs_solo"), team_map, "не вказано")

    # Q7 Monotony
    monotony_map = {"ok": "ок", "tired": "втомлює"}
    monotony_text = map_val(data.get("monotony_reaction"), monotony_map, "не вказано")

    # Q8 Risk
    risk_map = {"risk": "ризикую", "careful": "обережно", "stable": "стабільність"}
    risk_text = map_val(data.get("risk_style"), risk_map, "не вказано")

    # Q9 Learning
    learn_map = {"theory_first": "теорія", "practice_first": "практика", "people_first": "люди"}
    learn_text = map_val(data.get("learning_style"), learn_map, "не вказано")
    
    await message.answer("🔮 Створюю цифровий двійник...", parse_mode="Markdown")

    # Аналіз поведінки (Всі 10 питань)
    behavior_vector = await behavior_analyzer.analyze_survey_responses(
        chaos_vs_routine=chaos_text,
        deadline_reaction=deadline_text,
        emotional_trigger=data.get("emotional_trigger", ""),
        conflict_reaction=data.get("conflict_reaction", ""),
        social_energy=social_text,
        team_vs_solo=team_text,
        monotony_reaction=monotony_text,
        risk_style=risk_text,
        learning_style=learn_text,
        ideal_day=data.get("ideal_day", "")
    )
    
    # Зберігаємо
    await db.save_behavior_vector(
        user_id=message.from_user.id,
        chaos_tolerance=behavior_vector["chaos_tolerance"],
        routine_preference=behavior_vector["routine_preference"],
        decision_speed=behavior_vector["decision_speed"],
        risk_tendency=behavior_vector["risk_tendency"],
        social_communication=behavior_vector["social_communication"],
        emotional_triggers=behavior_vector["emotional_triggers"],
    )

    await state.update_data(behavior_vector=behavior_vector)

    # Показуємо рекомендовані ролі
    roles = behavior_vector.get(
        "recommended_roles",
        [
            "UX/UI Designer", "Data Analyst", "HR Specialist", "Backend Developer",
            "Project Manager", "Product Manager", "Business Analyst", "QA Engineer",
            "Sales Manager", "Customer Success Manager"
        ],
    )

    text = (
        "✅ **Двійник створено!**\n\n"
        "Обери професію для симуляції:"
    )

    keyboard_buttons = []
    role_emojis = {
        "UX/UI Designer": "🚀", "Data Analyst": "📊", "HR Specialist": "🧠",
        "Backend Developer": "💻", "Frontend Developer": "🌐", "Продакт-менеджер": "🎙",
        "Project Manager": "📅", "Product Manager": "🎯", "Business Analyst": "📈",
        "QA Engineer": "🧪", "Sales Manager": "💬", "Customer Success Manager": "🤝",
        "Digital Marketer": "📱", "Copywriter": "✍️", "SMM Specialist": "📸",
        "DevOps Engineer": "🔧", "Game Designer": "🎮", "Recruiter": "🔎",
        "Graphic Designer": "🎨", "Video Editor": "🎬",
    }

    # Зберігаємо ролі в стейт для доступу по індексу (уникнення BUTTON_DATA_INVALID)
    await state.update_data(recommended_roles=roles)

    # Беремо до 16 ролей
    for i, role in enumerate(roles[:16]):
        emoji = role_emojis.get(role, "📌")
        keyboard_buttons.append(
            [InlineKeyboardButton(text=f"{emoji} {role}", callback_data=f"role_idx_{i}")]
        )
    keyboard_buttons.append(
        [InlineKeyboardButton(text="✏️ Ввести свою професію", callback_data="custom_role")]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SimulationStates.waiting_role_selection)


async def _start_role_simulation(callback: CallbackQuery, state: FSMContext, role_name: str):
    """Спільна логіка запуску багатосерійної симуляції для ролі"""
    data = await state.get_data()
    behavior_vector = data.get("behavior_vector", {})
    
    # Надсилаємо нове повідомлення замість редагування старого
    loading_msg = await callback.message.answer(
        f"🔮 Генерую епізод: **{role_name}**...",
        parse_mode="Markdown",
    )
    await callback.answer()
    
    # Генеруємо перший епізод
    first_episode = await scenario_generator.generate_scenario(role_name, behavior_vector)
    
    # Ініціалізуємо серіал з епізодів та історією виборів
    await state.update_data(
        current_role=role_name,
        episodes=[first_episode],          # список епізодів
        current_episode_index=0,
        episode_choices=[],                # список обраних опцій по епізодах
    )
    
    # Формуємо повідомлення з першим епізодом
    scenario = first_episode
    text = (
        f"🔮 **Роль: {role_name}**\n\n"
        f"**Епізод 1:**\n{scenario['scenario_description']}\n\n"
        f"**Як ти відреагуєш?**"
    )
    
    keyboard_buttons = []
    for option in scenario["options"]:
        keyboard_buttons.append(
            [
                InlineKeyboardButton(
                    text=option["text"],
                    callback_data=f"sim_option_{option['id']}",
                )
            ]
        )
    # Додаємо можливість написати свій варіант реакції
    keyboard_buttons.append(
        [InlineKeyboardButton(text="✏️ Написати свій варіант", callback_data="sim_option_custom")]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await loading_msg.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SimulationStates.waiting_simulation_episode_response)


@router.callback_query(F.data.startswith("role_idx_"), SimulationStates.waiting_role_selection)
async def start_simulation(callback: CallbackQuery, state: FSMContext):
    """Початок багатосерійної симуляції для обраної з кнопки ролі (за індексом)"""
    try:
        idx = int(callback.data.replace("role_idx_", ""))
        data = await state.get_data()
        roles = data.get("recommended_roles", [])
        
        if 0 <= idx < len(roles):
            role_name = roles[idx]
            await _start_role_simulation(callback, state, role_name)
        else:
            await callback.answer("Помилка: Роль не знайдена", show_alert=True)
    except (ValueError, TypeError):
        await callback.answer("Помилка обробки вибору", show_alert=True)


@router.callback_query(F.data == "custom_role", SimulationStates.waiting_role_selection)
async def ask_custom_role(callback: CallbackQuery, state: FSMContext):
    """Запит користувача ввести свою професію текстом"""
    await callback.answer()
    await callback.message.edit_text(
        "✏️ Напиши, будь ласка, назву професії або ролі, яку ти хочеш протестувати.\n\n"
        "Наприклад: «Product Owner», «Психолог», «Маркетолог», «3D Artist» тощо.",
        parse_mode="Markdown",
    )
    await state.set_state(SimulationStates.waiting_custom_role)


@router.message(SimulationStates.waiting_custom_role)
async def start_simulation_custom_role(message: Message, state: FSMContext):
    """Початок симуляції для довільно введеної користувачем ролі"""
    role_name = message.text.strip()
    if not role_name:
        await message.answer("Будь ласка, введи хоч якусь назву ролі 🙂")
        return

    # Обертаємо у фейковий callback для повторного використання логіки
    class _MsgWrapper:
        def __init__(self, msg: Message):
            self.message = msg

        async def answer(self):  # для сумісності з _start_role_simulation
            return

    fake_cb = _MsgWrapper(message)
    await _start_role_simulation(fake_cb, state, role_name)


@router.callback_query(F.data.startswith("sim_option_"), SimulationStates.waiting_simulation_episode_response)
async def process_simulation_episode(callback: CallbackQuery, state: FSMContext):
    """Обробка відповіді на поточний епізод симуляції"""
    option_id = callback.data.replace("sim_option_", "")
    data = await state.get_data()

    # Якщо користувач хоче написати свій варіант — просимо ввести текст
    if option_id == "custom":
        await callback.message.answer(
            "✏️ Як би ти відреагував(ла)? (кілька слів)."
        )
        await callback.answer()
        await state.set_state(SimulationStates.waiting_custom_episode_response)
        return
    
    episodes = data.get("episodes", [])
    current_index = int(data.get("current_episode_index", 0))
    scenario = episodes[current_index] if 0 <= current_index < len(episodes) else {}
    behavior_vector = data.get("behavior_vector", {})
    role_name = data.get("current_role", "")
    
    # Знаходимо текст обраного варіанту
    selected_option_text = ""
    for option in scenario.get("options", []):
        if option["id"] == option_id:
            selected_option_text = option["text"]
            break

    # Записуємо вибір користувача для цього епізоду
    episode_choices = data.get("episode_choices", [])
    episode_choices.append(
        {
            "episode_index": current_index,
            "scenario_description": scenario.get("scenario_description", ""),
            "selected_option_id": option_id,
            "selected_option_text": selected_option_text,
            "stress_factors": scenario.get("stress_factors", []),
        }
    )

    await state.update_data(
        episode_choices=episode_choices,
    )

    # Вирішуємо: згенерувати наступний епізод чи завершити серіал
    MAX_EPISODES = 3
    next_index = current_index + 1

    if next_index < MAX_EPISODES:
        # Генеруємо наступний епізод з урахуванням попередніх виборів
        await callback.message.edit_text(
            "🔄 Генерую наступний епізод...",
            parse_mode="Markdown",
        )
        await callback.answer()

        next_episode = await scenario_generator.generate_scenario(role_name, behavior_vector)
        episodes.append(next_episode)
        await state.update_data(
            episodes=episodes,
            current_episode_index=next_index,
        )

        text = (
            f"🔮 **Епізод {next_index + 1} із {MAX_EPISODES}**\n\n"
            f"**Сценарій:**\n{next_episode['scenario_description']}\n\n"
            f"**Як ти відреагуєш?**"
        )

        keyboard_buttons = []
        for option in next_episode["options"]:
            keyboard_buttons.append(
                [
                    InlineKeyboardButton(
                        text=option["text"],
                        callback_data=f"sim_option_{option['id']}",
                    )
                ]
            )
        # Додаємо можливість написати свій варіант реакції
        keyboard_buttons.append(
            [InlineKeyboardButton(text="✏️ Написати свій варіант", callback_data="sim_option_custom")]
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(SimulationStates.waiting_simulation_episode_response)
        return

    # Якщо це був фінальний епізод — робимо підсумковий аналіз усієї історії
    await callback.message.edit_text("📈 Формую фінальний звіт...", parse_mode="Markdown")
    await callback.answer()

    # Поки що передаємо останній епізод у BurnoutPredictor,
    # але в prompt уже можна буде додати контекст усіх епізодів.
    last_episode = scenario
    analysis = await burnout_predictor.analyze_simulation_response(
        role_name=role_name,
        behavior_vector=behavior_vector,
        scenario_description=last_episode.get("scenario_description", ""),
        selected_option=option_id,
        option_text=selected_option_text,
    )

    # Зберігаємо результат
    await db.save_simulation_result(
        user_id=callback.from_user.id,
        role_name=role_name,
        compatibility_score=analysis["compatibility_score"],
        burnout_risk=analysis["burnout_risk"],
        strengths=analysis["strengths"],
        weaknesses=analysis["weaknesses"],
        recommendations=analysis["recommendations"],
    )

    burnout_emoji = {
        "низький": "🟢",
        "середній": "🟡",
        "високий": "🔴",
    }
    emoji = burnout_emoji.get(analysis["burnout_risk"], "🟡")

    text = (
        f"📊 **Звіт Career-Twin: {role_name}**\n\n"
        f"**Сумісність:** {analysis['compatibility_score']}%\n"
        f"**Burnout-ризик:** {emoji} {analysis['burnout_risk'].capitalize()}\n\n"
        f"**Сильні сторони:**\n{analysis['strengths']}\n\n"
        f"**Потенційні проблеми:**\n{analysis['weaknesses']}\n\n"
        f"**Рекомендації:**\n{analysis['recommendations']}\n\n"
        f"**Тригери цієї ролі (останній епізод):** {', '.join(last_episode.get('stress_factors', []))}"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Спробувати іншу роль", callback_data="start_survey")],
            [InlineKeyboardButton(text="✅ Завершити", callback_data="back_to_start")],
        ]
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SimulationStates.simulation_finished)


@router.message(SimulationStates.waiting_custom_episode_response)
async def process_custom_episode_response(message: Message, state: FSMContext):
    """Обробка текстової відповіді користувача на епізод (власний варіант)"""
    data = await state.get_data()

    episodes = data.get("episodes", [])
    current_index = int(data.get("current_episode_index", 0))
    scenario = episodes[current_index] if 0 <= current_index < len(episodes) else {}
    behavior_vector = data.get("behavior_vector", {})
    role_name = data.get("current_role", "")

    selected_option_text = message.text.strip()
    option_id = "custom"

    # Записуємо вибір користувача для цього епізоду
    episode_choices = data.get("episode_choices", [])
    episode_choices.append(
        {
            "episode_index": current_index,
            "scenario_description": scenario.get("scenario_description", ""),
            "selected_option_id": option_id,
            "selected_option_text": selected_option_text,
            "stress_factors": scenario.get("stress_factors", []),
        }
    )

    await state.update_data(
        episode_choices=episode_choices,
    )

    # Вирішуємо: згенерувати наступний епізод чи завершити серіал
    MAX_EPISODES = 3
    next_index = current_index + 1

    if next_index < MAX_EPISODES:
        await message.answer(
            "🔄 Генерую наступний епізод...",
            parse_mode="Markdown",
        )

        next_episode = await scenario_generator.generate_scenario(role_name, behavior_vector)
        episodes.append(next_episode)
        await state.update_data(
            episodes=episodes,
            current_episode_index=next_index,
        )

        text = (
            f"🔮 **Епізод {next_index + 1} із {MAX_EPISODES}**\n\n"
            f"**Сценарій:**\n{next_episode['scenario_description']}\n\n"
            f"**Як ти відреагуєш?**"
        )

        keyboard_buttons = []
        for option in next_episode["options"]:
            keyboard_buttons.append(
                [
                    InlineKeyboardButton(
                        text=option["text"],
                        callback_data=f"sim_option_{option['id']}",
                    )
                ]
            )
        keyboard_buttons.append(
            [
                InlineKeyboardButton(
                    text="✏️ Написати свій варіант",
                    callback_data="sim_option_custom",
                )
            ]
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(SimulationStates.waiting_simulation_episode_response)
        return

    # Якщо це був фінальний епізод — робимо підсумковий аналіз усієї історії
    await message.answer(
        "📈 Аналізую всю історію реакцій та прогнозую ризик вигорання...",
        parse_mode="Markdown",
    )

    last_episode = scenario
    analysis = await burnout_predictor.analyze_simulation_response(
        role_name=role_name,
        behavior_vector=behavior_vector,
        scenario_description=last_episode.get("scenario_description", ""),
        selected_option=option_id,
        option_text=selected_option_text,
    )

    # Зберігаємо результат
    await db.save_simulation_result(
        user_id=message.from_user.id,
        role_name=role_name,
        compatibility_score=analysis["compatibility_score"],
        burnout_risk=analysis["burnout_risk"],
        strengths=analysis["strengths"],
        weaknesses=analysis["weaknesses"],
        recommendations=analysis["recommendations"],
    )

    burnout_emoji = {
        "низький": "🟢",
        "середній": "🟡",
        "високий": "🔴",
    }
    emoji = burnout_emoji.get(analysis["burnout_risk"], "🟡")

    text = (
        f"📊 **Звіт Career-Twin: {role_name} — завершення серіалу**\n\n"
        f"**Сумісність:** {analysis['compatibility_score']}%\n"
        f"**Burnout-ризик:** {emoji} {analysis['burnout_risk'].capitalize()}\n\n"
        f"**Сильні сторони:**\n{analysis['strengths']}\n\n"
        f"**Потенційні проблеми:**\n{analysis['weaknesses']}\n\n"
        f"**Рекомендації:**\n{analysis['recommendations']}\n\n"
        f"**Тригери цієї ролі (останній епізод):** {', '.join(last_episode.get('stress_factors', []))}"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Спробувати іншу роль", callback_data="start_survey")],
            [InlineKeyboardButton(text="✅ Завершити", callback_data="back_to_start")],
        ]
    )

    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SimulationStates.simulation_finished)


@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    """Повернення до початку"""
    await state.clear()
    await cmd_start(callback.message, state)

