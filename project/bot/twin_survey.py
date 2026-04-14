"""
Розширена анкета для створення цифрового двійника (BehaviorSurvey).
Команда запуску: /twin
"""

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from ai_engine.behavior_analyzer import BehaviorAnalyzer
from database import Database
from bot.states import SimulationStates


router = Router()
db = Database()
behavior_analyzer = BehaviorAnalyzer()


class BehaviorSurvey(StatesGroup):
    chaos_routine = State()
    free_time = State()
    soft_deadline = State()
    quality_vs_time = State()
    criticism = State()
    burnout_situation = State()
    social_energy = State()
    team_vs_solo = State()
    new_role = State()
    responsibility_vs_control = State()
    monotony = State()
    single_vs_multi_task = State()
    ideal_day = State()
    done = State()


@router.message(F.text == "⬅️ Назад")
async def back_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == BehaviorSurvey.free_time.state:
        await state.set_state(BehaviorSurvey.chaos_routine)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Мені ок, підлаштуюсь по ходу")],
                [KeyboardButton(text="Мене це виводить з рівноваги, люблю стабільність")],
            ], resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer("1/12. Уяви, що твій розклад раптово змінюється тричі за день.\nЩо тебе більше описує?", reply_markup=kb)

    elif current_state == BehaviorSurvey.soft_deadline.state:
        await state.set_state(BehaviorSurvey.free_time)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Придумую нову активність на ходу")],
                [KeyboardButton(text="Дістаю список запланованих справ")],
                [KeyboardButton(text="⬅️ Назад")],
            ], resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer("2/12. Якщо в тебе є 2 години вільного часу, ти скоріше…", reply_markup=kb)

    elif current_state == BehaviorSurvey.quality_vs_time.state:
        await state.set_state(BehaviorSurvey.soft_deadline)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Сам(а) ставлю собі дедлайн і план")],
                [KeyboardButton(text="Тягну до останнього, поки не стане терміново")],
                [KeyboardButton(text="⬅️ Назад")],
            ], resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer("3/12. Коли дають завдання «на потім» без чіткого дедлайну, ти…", reply_markup=kb)

    elif current_state == BehaviorSurvey.criticism.state:
        await state.set_state(BehaviorSurvey.quality_vs_time)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Здати вчасно, але середньо")],
                [KeyboardButton(text="Запізнитись, але зробити ідеально")],
                [KeyboardButton(text="⬅️ Назад")],
            ], resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer("4/12. Що для тебе гірше?", reply_markup=kb)

    elif current_state == BehaviorSurvey.burnout_situation.state:
        await state.set_state(BehaviorSurvey.criticism)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Мовчу, але всередині закипаю")],
                [KeyboardButton(text="Ставлю уточнюючі питання")],
                [KeyboardButton(text="Відстоюю свою позицію")],
                [KeyboardButton(text="⬅️ Назад")],
            ], resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer("5/12. Як ти реагуєш, коли хтось різко критикує твою роботу при інших?", reply_markup=kb)

    elif current_state == BehaviorSurvey.social_energy.state:
        await state.set_state(BehaviorSurvey.burnout_situation)
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⬅️ Назад")]],
            resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer("6/12. Опиши останню ситуацію, коли ти відчував(ла) сильне виснаження на роботі/навчанні. Що саме тебе «добило» найбільше?", reply_markup=kb)

    elif current_state == BehaviorSurvey.team_vs_solo.state:
        await state.set_state(BehaviorSurvey.social_energy)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Почуваюсь зарядженою/зарядженим")],
                [KeyboardButton(text="Хочу ні з ким не говорити кілька годин")],
                [KeyboardButton(text="⬅️ Назад")],
            ], resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer("7/12. Після дня, повного спілкування, ти зазвичай…", reply_markup=kb)

    elif current_state == BehaviorSurvey.new_role.state:
        await state.set_state(BehaviorSurvey.team_vs_solo)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Постійно обговорювати ідеї в команді")],
                [KeyboardButton(text="Отримати задачу і робити її наодинці")],
                [KeyboardButton(text="⬅️ Назад")],
            ], resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer("8/12. Що для тебе комфортніше в роботі?", reply_markup=kb)

    elif current_state == BehaviorSurvey.responsibility_vs_control.state:
        await state.set_state(BehaviorSurvey.new_role)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Кажу «так», а розберусь по дорозі")],
                [KeyboardButton(text="Відмовляюсь, поки не буду готовий(а)")],
                [KeyboardButton(text="⬅️ Назад")],
            ], resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer("9/12. Тобі пропонують нову роль/проєкт, де ти майже нічого не знаєш. Ти…", reply_markup=kb)

    elif current_state == BehaviorSurvey.monotony.state:
        await state.set_state(BehaviorSurvey.responsibility_vs_control)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Взяти забагато відповідальності")],
                [KeyboardButton(text="Взагалі не мати впливу на результат")],
                [KeyboardButton(text="⬅️ Назад")],
            ], resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer("10/12. Що тебе лякає більше?", reply_markup=kb)

    elif current_state == BehaviorSurvey.single_vs_multi_task.state:
        await state.set_state(BehaviorSurvey.monotony)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Це ок, навіть заспокоює")],
                [KeyboardButton(text="Швидко втрачаю фокус і відволікаюсь")],
                [KeyboardButton(text="⬅️ Назад")],
            ], resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer("11/12. Як ти реагуєш на задачі, де 2–3 години треба робити одне й те саме?", reply_markup=kb)

    elif current_state == BehaviorSurvey.ideal_day.state:
        await state.set_state(BehaviorSurvey.single_vs_multi_task)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Одну велику задачу до кінця")],
                [KeyboardButton(text="3–4 різні задачі, постійно перемикаючись")],
                [KeyboardButton(text="⬅️ Назад")],
            ], resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer("12/12. Що тобі легше?", reply_markup=kb)


@router.message(F.text == "/twin")
async def start_survey(message: Message, state: FSMContext):
    """Старт розширеної поведінкової анкети по команді /twin"""
    await state.clear()
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мені ок, підлаштуюсь по ходу")],
            [KeyboardButton(text="Мене це виводить з рівноваги, люблю стабільність")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "1/12. Уяви, що твій розклад раптово змінюється тричі за день.\n"
        "Що тебе більше описує?",
        reply_markup=kb,
    )
    await state.set_state(BehaviorSurvey.chaos_routine)


@router.message(BehaviorSurvey.chaos_routine)
async def q2_free_time(message: Message, state: FSMContext):
    await state.update_data(chaos_routine=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Придумую нову активність на ходу")],
            [KeyboardButton(text="Дістаю список запланованих справ")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "2/12. Якщо в тебе є 2 години вільного часу, ти скоріше…",
        reply_markup=kb,
    )
    await state.set_state(BehaviorSurvey.free_time)


@router.message(BehaviorSurvey.free_time)
async def q3_soft_deadline(message: Message, state: FSMContext):
    await state.update_data(free_time=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сам(а) ставлю собі дедлайн і план")],
            [KeyboardButton(text="Тягну до останнього, поки не стане терміново")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "3/12. Коли дають завдання «на потім» без чіткого дедлайну, ти…",
        reply_markup=kb,
    )
    await state.set_state(BehaviorSurvey.soft_deadline)


@router.message(BehaviorSurvey.soft_deadline)
async def q4_quality_vs_time(message: Message, state: FSMContext):
    await state.update_data(soft_deadline=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Здати вчасно, але середньо")],
            [KeyboardButton(text="Запізнитись, але зробити ідеально")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "4/12. Що для тебе гірше?",
        reply_markup=kb,
    )
    await state.set_state(BehaviorSurvey.quality_vs_time)


@router.message(BehaviorSurvey.quality_vs_time)
async def q5_criticism(message: Message, state: FSMContext):
    await state.update_data(quality_vs_time=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мовчу, але всередині закипаю")],
            [KeyboardButton(text="Ставлю уточнюючі питання")],
            [KeyboardButton(text="Відстоюю свою позицію")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "5/12. Як ти реагуєш, коли хтось різко критикує твою роботу при інших?",
        reply_markup=kb,
    )
    await state.set_state(BehaviorSurvey.criticism)


@router.message(BehaviorSurvey.criticism)
async def q6_burnout_situation(message: Message, state: FSMContext):
    await state.update_data(criticism=message.text)
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    
    await message.answer(
        "6/12. Опиши останню ситуацію, коли ти відчував(ла) сильне виснаження "
        "на роботі/навчанні. Що саме тебе «добило» найбільше?",
        reply_markup=kb,
    )
    await state.set_state(BehaviorSurvey.burnout_situation)


@router.message(BehaviorSurvey.burnout_situation)
async def q7_social_energy(message: Message, state: FSMContext):
    await state.update_data(burnout_situation=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Почуваюсь зарядженою/зарядженим")],
            [KeyboardButton(text="Хочу ні з ким не говорити кілька годин")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "7/12. Після дня, повного спілкування, ти зазвичай…",
        reply_markup=kb,
    )
    await state.set_state(BehaviorSurvey.social_energy)


@router.message(BehaviorSurvey.social_energy)
async def q8_team_vs_solo(message: Message, state: FSMContext):
    await state.update_data(social_energy=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Постійно обговорювати ідеї в команді")],
            [KeyboardButton(text="Отримати задачу і робити її наодинці")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "8/12. Що для тебе комфортніше в роботі?",
        reply_markup=kb,
    )
    await state.set_state(BehaviorSurvey.team_vs_solo)


@router.message(BehaviorSurvey.team_vs_solo)
async def q9_new_role(message: Message, state: FSMContext):
    await state.update_data(team_vs_solo=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Кажу «так», а розберусь по дорозі")],
            [KeyboardButton(text="Відмовляюсь, поки не буду готовий(а)")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "9/12. Тобі пропонують нову роль/проєкт, де ти майже нічого не знаєш. Ти…",
        reply_markup=kb,
    )
    await state.set_state(BehaviorSurvey.new_role)


@router.message(BehaviorSurvey.new_role)
async def q10_responsibility_vs_control(message: Message, state: FSMContext):
    await state.update_data(new_role=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Взяти забагато відповідальності")],
            [KeyboardButton(text="Взагалі не мати впливу на результат")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "10/12. Що тебе лякає більше?",
        reply_markup=kb,
    )
    await state.set_state(BehaviorSurvey.responsibility_vs_control)


@router.message(BehaviorSurvey.responsibility_vs_control)
async def q11_monotony(message: Message, state: FSMContext):
    await state.update_data(responsibility_vs_control=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Це ок, навіть заспокоює")],
            [KeyboardButton(text="Швидко втрачаю фокус і відволікаюсь")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "11/12. Як ти реагуєш на задачі, де 2–3 години треба робити одне й те саме?",
        reply_markup=kb,
    )
    await state.set_state(BehaviorSurvey.monotony)


@router.message(BehaviorSurvey.monotony)
async def q12_single_vs_multi_task(message: Message, state: FSMContext):
    await state.update_data(monotony=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Одну велику задачу до кінця")],
            [KeyboardButton(text="3–4 різні задачі, постійно перемикаючись")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "12/12. Що тобі легше?",
        reply_markup=kb,
    )
    await state.set_state(BehaviorSurvey.single_vs_multi_task)


@router.message(BehaviorSurvey.single_vs_multi_task)
async def q13_ideal_day(message: Message, state: FSMContext):
    await state.update_data(single_vs_multi_task=message.text)
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    
    await message.answer(
        "13/13. І останнє: опиши одним реченням свій «ідеальний робочий день» через 2-3 роки.",
        reply_markup=kb,
    )
    await state.set_state(BehaviorSurvey.ideal_day)


@router.message(BehaviorSurvey.ideal_day)
async def survey_finish(message: Message, state: FSMContext):
    """Фініш анкети: тут викликаємо LLM для аналізу поведінкового вектору"""
    await state.update_data(ideal_day=message.text)
    data = await state.get_data()

    await message.answer("🔮 Аналізую твої відповіді та створюю цифровий двійник...", parse_mode="Markdown")

    # Аналіз за всіма 13 питаннями
    behavior_vector = await behavior_analyzer.analyze_survey_responses(
        chaos_vs_routine=data.get("chaos_routine", ""),
        deadline_reaction=data.get("soft_deadline", ""),
        emotional_trigger=data.get("burnout_situation", ""),
        conflict_reaction=f"{data.get('criticism', '')}. {data.get('responsibility_vs_control', '')}",
        social_energy=data.get("social_energy", ""),
        team_vs_solo=data.get("team_vs_solo", ""),
        monotony_reaction=data.get("monotony", ""),
        risk_style=data.get("new_role", ""),
        learning_style=f"{data.get('free_time', '')}. {data.get('single_vs_multi_task', '')}",
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
    roles = behavior_vector.get("recommended_roles", [])

    text = (
        "✅ **Двійник створено!**\n\n"
        "Я проаналізував твій Поведінковий Вектор на основі розширеної анкети. "
        "Тепер обери професію для симуляції:\n\n"
    )

    # Зберігаємо ролі в стейт для доступу по індексу
    await state.update_data(recommended_roles=roles)

    # Спроба додати емодзі до ролей для краси
    role_emojis = {
        "Designer": "🎨", "Developer": "💻", "Manager": "📊", "Analyst": "📈",
        "Engineer": "🔧", "Specialist": "📌", "Marketer": "📱", "Writer": "✍️"
    }

    keyboard_buttons = []
    for i, role in enumerate(roles[:5]):
        emoji = "📌"
        for keyword, e in role_emojis.items():
            if keyword.lower() in role.lower():
                emoji = e
                break
        keyboard_buttons.append(
            [InlineKeyboardButton(text=f"{emoji} {role}", callback_data=f"role_idx_{i}")]
        )
    
    keyboard_buttons.append(
        [InlineKeyboardButton(text="✏️ Ввести свою професію", callback_data="custom_role")]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(SimulationStates.waiting_role_selection)
