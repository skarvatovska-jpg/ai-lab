import os

path = r"c:\Users\329\Documents\ai-lab\project\bot\handlers.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add back button to standard custom answer rows
lines = content.split('\n')
new_lines = []
in_survey = False

for line in lines:
    if '@router.callback_query(F.data == "start_survey")' in line:
        in_survey = True

    if "def _finalize_survey" in line:
        in_survey = False
        
    if in_survey and 'text="✏️ Своя відповідь"' in line:
        if line.strip().endswith(','):
            new_lines.append(line)
        else:
            new_lines.append(line + ',')
        
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(indent + '[InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]')
    else:
        new_lines.append(line)

content = '\n'.join(new_lines)


# 2. Add back handler code
back_handler = """

@router.callback_query(F.data == "survey_back")
async def process_survey_back(callback: CallbackQuery, state: FSMContext):
    current = await state.get_state()
    
    if current in (SurveyStates.waiting_deadline.state, SurveyStates.waiting_q1_custom.state):
        await start_survey(callback, state)
        
    elif current in (SurveyStates.waiting_emotional_trigger.state, SurveyStates.waiting_q2_custom.state):
        text = "**2/10. Дедлайни та свобода**\\n\\nУяви задачу на кілька днів. Як тобі комфортніше працювати з нею?"
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
        text = "**3/10. Емоційний тригер**\\n\\nЩо найбільше виснажує тебе на роботі/навчанні? (наприклад: дедлайни, тиск)."
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(SurveyStates.waiting_emotional_trigger)
        
    elif current in (SurveyStates.waiting_q5.state, SurveyStates.waiting_q5_custom.state):
        text = "**4/10. Реакція в конфлікті**\\n\\nКолега/клієнт публічно незадоволений твоєю роботою. Твої дії?"
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
        text = "**5/10. Після повного дня спілкування**\\n\\nЯк ти почуваєшся після дня, коли було багато зустрічей, дзвінків і взаємодії з людьми?"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔋 Відчуваю заряд енергії", callback_data="q5_charged")],
            [InlineKeyboardButton(text="🔌 Вимотаний(а), хочу тиші і усамітнення", callback_data="q5_drained")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q5_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(SurveyStates.waiting_q5)
        
    elif current in (SurveyStates.waiting_q7.state, SurveyStates.waiting_q7_custom.state):
        text = "**6/10. Команда чи соло**\\n\\nУяви, що тобі дають складну задачу. Як тобі комфортніше її вирішувати?"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 В команді, з обговореннями та брейнштормами", callback_data="q6_team")],
            [InlineKeyboardButton(text="👤 Наодинці, у своєму ритмі", callback_data="q6_solo")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q6_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(SurveyStates.waiting_q6)
        
    elif current in (SurveyStates.waiting_q8.state, SurveyStates.waiting_q8_custom.state):
        text = "**7/10. Рутинні задачі**\\n\\nЯк ти ставишся до задач, де потрібно багато разів повторювати одну й ту саму дію?"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="😌 Це ок, навіть заспокоює", callback_data="q7_ok")],
            [InlineKeyboardButton(text="😵 Дуже швидко втомлююсь і відволікаюсь", callback_data="q7_tired")],
            [InlineKeyboardButton(text="✏️ Своя відповідь", callback_data="q7_custom")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(SurveyStates.waiting_q7)
        
    elif current in (SurveyStates.waiting_q9.state, SurveyStates.waiting_q9_custom.state):
        text = "**8/10. Нові можливості та ризик**\\n\\nТобі пропонують ризиковий проєкт з великим потенціалом. Як реагуєш?"
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
        text = "**9/10. Стиль навчання**\\n\\nЯк ти зазвичай вивчаєш щось нове?"
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
"""

content = content.replace("async def _finalize_survey(message: Message, state: FSMContext):", back_handler + "\nasync def _finalize_survey(message: Message, state: FSMContext):")

# Fix Text-only Prompts (Q3 and Q10)
content = content.replace('await callback.message.edit_text(text, parse_mode="Markdown")\n    await callback.answer()\n    await state.set_state(SurveyStates.waiting_emotional_trigger)',
                          'keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]])\n    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")\n    await callback.answer()\n    await state.set_state(SurveyStates.waiting_emotional_trigger)')


content = content.replace('await message.answer(text, parse_mode="Markdown")\n    await state.set_state(SurveyStates.waiting_emotional_trigger)',
                          'keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]])\n    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")\n    await state.set_state(SurveyStates.waiting_emotional_trigger)')

content = content.replace('await callback.message.edit_text(text, parse_mode="Markdown")\n    await callback.answer()\n    await state.set_state(SurveyStates.waiting_q10)',
                          'keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]])\n    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")\n    await callback.answer()\n    await state.set_state(SurveyStates.waiting_q10)')

content = content.replace('await message.answer(text, parse_mode="Markdown")\n    await state.set_state(SurveyStates.waiting_q10)',
                          'keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="survey_back")]])\n    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")\n    await state.set_state(SurveyStates.waiting_q10)')

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("done")
