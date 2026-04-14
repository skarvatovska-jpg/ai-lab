"""
Модуль для генерації професійних сценаріїв та симуляцій
"""
import json
from typing import Dict, Any, List
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL


class ScenarioGenerator:
    """Клас для генерації професійних сценаріїв"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    async def generate_scenario(
        self,
        role_name: str,
        behavior_vector: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Генерує сценарій симуляції для конкретної професії.

        Сценарій має бути не абстрактним описом роботи,
        а однією конкретною ситуацією в робочий день,
        описаною від ПЕРШОЇ особи (ніби користувач сам розповідає «я…»):
        - де відбувається дія (тип компанії, команда, контекст);
        - що саме сталося (подія / проблема / конфлікт);
        - які є обмеження (час, ресурси, люди);
        - що поставлено на кону (наслідки для користувача / команди / бізнесу).
        
        Returns:
            Dict з полями:
            - scenario_description: str (дуже короткий опис ситуації, 1–2 речення)
            - options: List[Dict] з полями text, id
            - stress_factors: List[str] (ключові стресові фактори)
        """
        
        system_prompt = """Ти експерт з кар'єрної орієнтації та професійної симуляції.
Твоя задача — створити максимально стислий, конкретний сценарій робочої ситуації (max 2 короткі речення)
для симуляції БУДЬ-ЯКОЇ професійної ролі.

Сценарій має бути СЦЕНОЮ з життя, описаною від ПЕРШОЇ ОСОБИ (\"я\"). 
Він повинен відображати реальні виклики та контекст саме тієї професії, яку вказав користувач.
Не використовуй звертання до читача типу \"ти\", \"вас\".

1) Задай контекст і конфлікт одним коротким абзацом (1-2 речення).
2) Ситуація має бути максимально специфічною для вказаної професії.
3) Поверни JSON з такими полями:
- scenario_description: string (СТИСЛИЙ опис сцени, максимум 2 короткі речення, ВІД ПЕРШОЇ ОСОБИ: \"я...\" )
- options: array з 4 об'єктів, кожен має поля:
  - text: string (ДУЖЕ КОРОТКИЙ варіант дії, до 10 слів, ВІД ПЕРШОЇ ОСОБИ: \"я ...\")
  - id: string (короткий ідентифікатор, наприклад "option_1")
  Структура варіантів: 1 — емоційна; 2 — раціональна; 3 — дипломатична; 4 — уникнення.
- stress_factors: array з рядками (1-2 ключові фактори).

Важливо: ПИШИ МАКСИМАЛЬНО КОРОТКО."""
        
        user_prompt = f"""Створи чіткий, вузькоспеціалізований сценарій симуляції для ролі: {role_name}

Поведінковий профіль користувача (використовуй для адаптації складності ситуації):
- Толерантність до хаосу: {behavior_vector.get('chaos_tolerance', 0.5):.2f}
- Схильність до рутини: {behavior_vector.get('routine_preference', 0.5):.2f}
- Швидкість прийняття рішень: {behavior_vector.get('decision_speed', 0.5):.2f}
- Схильність до ризику: {behavior_vector.get('risk_tendency', 0.5):.2f}
- Соціальна комунікабельність: {behavior_vector.get('social_communication', 0.5):.2f}

Покажи ситуацію, яка могла б реально трапитися саме у {role_name}, і яка змусить користувача проявити свої поведінкові риси."""

        try:
            print(f"DEBUG: Generating scenario for role: {role_name}")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            print(f"DEBUG: AI response: {result_text[:100]}...")
            result = json.loads(result_text)

            # Додаткова перевірка: якщо LLM повернув пустий або занадто короткий сценарій
            if not result.get("scenario_description") or len(result.get("scenario_description")) < 10:
                raise ValueError("AI returned empty or too short scenario description")

            return {
                "scenario_description": result.get("scenario_description", ""),
                "options": result.get("options", []),
                "stress_factors": result.get("stress_factors", []),
            }
            
        except Exception as e:
            print(f"ERROR in generate_scenario for {role_name}: {e}")
            # Повертаємо більш реалістичний заготовлений сценарій у разі помилки
            return {
                "scenario_description": (
                    f"Ти працюєш на позиції {role_name} у продуктовій компанії. "
                    "У другій половині дня до тебе приходить керівник і просить терміново "
                    "підготувати результат по важливому проєкту до вечірнього дзвінка з клієнтом, "
                    "хоча ти вже забитий(а) іншими задачами. Паралельно з'ясовується, що в поточному "
                    "проєкті виявили критичну помилку, і команда очікує, що ти допоможеш її розв'язати "
                    "протягом найближчої години."
                ),
                "options": [
                    {
                        "text": (
                            "Зосереджуюсь на запиті керівника, відкладаючи інші задачі, "
                            "і намагаюсь сам(а) закрити максимум до дзвінка, працюючи на межі ресурсу."
                        ),
                        "id": "option_1",
                    },
                    {
                        "text": (
                            "Проговорю з керівником і командою поточне навантаження, "
                            "перепогоджую пріоритети та прошу перерозподілити частину задач."
                        ),
                        "id": "option_2",
                    },
                    {
                        "text": (
                            "Берусь спочатку за виправлення критичної помилки, а задачі для клієнта "
                            "роблю по мінімуму, сподіваючись, що цього буде достатньо для дзвінка."
                        ),
                        "id": "option_3",
                    },
                ],
                "stress_factors": [
                    "жорсткий дедлайн",
                    "перевантаження завданнями",
                    "конфлікт пріоритетів",
                ],
            }

