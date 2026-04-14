"""
Модуль для аналізу поведінкових відповідей та формування поведінкового вектора
"""
import json
from typing import Dict, Any, List
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL


class BehaviorAnalyzer:
    """Клас для аналізу поведінки користувача"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    async def analyze_survey_responses(
        self,
        chaos_vs_routine: str,
        deadline_reaction: str,
        emotional_trigger: str,
        conflict_reaction: str,
        social_energy: str,
        team_vs_solo: str,
        monotony_reaction: str,
        risk_style: str,
        learning_style: str,
        ideal_day: str
    ) -> Dict[str, Any]:
        """
        Аналізує відповіді анкети та формує поведінковий вектор (аналог Big5)
        
        Returns:
            Dict з полями:
            - chaos_tolerance: float (0-1)
            - routine_preference: float (0-1)
            - decision_speed: float (0-1)
            - risk_tendency: float (0-1)
            - social_communication: float (0-1)
            - emotional_triggers: str
            - recommended_roles: List[str] (5 професій)
        """
        
        system_prompt = """Ти експерт з психології поведінки та кар'єрної орієнтації. 
Твоя задача - проаналізувати відповіді користувача та сформувати поведінковий вектор 
за аналогією з моделлю Big Five (Велика п'ятірка особистісних характеристик).

Проаналізуй відповіді та поверни JSON з такими полями:
- chaos_tolerance: float від 0 до 1 (толерантність до хаосу та невизначеності)
- routine_preference: float від 0 до 1 (схильність до рутини та структури)
- decision_speed: float від 0 до 1 (швидкість прийняття рішень)
- risk_tendency: float від 0 до 1 (схильність до ризику)
- social_communication: float від 0 до 1 (соціальна комунікабельність)
- emotional_triggers: string (дуже коротко, одним-двома словами описати емоційні тригери)
- recommended_roles: список з 5 професій (українською мовою).

Важливо: поверни ТІЛЬКИ валідний JSON без додаткових пояснень. Пиши максимально стисло. """

        user_prompt = f"""Відповіді користувача на розширену анкету:

1. Хаос vs Рутина: {chaos_vs_routine}
2. Реакція на дедлайни: {deadline_reaction}
3. Емоційний тригер (що виснажує): {emotional_trigger}
4. Реакція в конфлікті / на критику: {conflict_reaction}
5. Енергія після спілкування: {social_energy}
6. Команда чи соло: {team_vs_solo}
7. Ставлення до монотонності: {monotony_reaction}
8. Стиль ризику: {risk_style}
9. Стиль навчання: {learning_style}
10. Ідеальний день: {ideal_day}

Проаналізуй та поверни поведінковий вектор у форматі JSON."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # Валідація та нормалізація значень
            behavior_vector = {
                "chaos_tolerance": float(result.get("chaos_tolerance", 0.5)),
                "routine_preference": float(result.get("routine_preference", 0.5)),
                "decision_speed": float(result.get("decision_speed", 0.5)),
                "risk_tendency": float(result.get("risk_tendency", 0.5)),
                "social_communication": float(result.get("social_communication", 0.5)),
                "emotional_triggers": result.get("emotional_triggers", ""),
                "recommended_roles": result.get("recommended_roles", [])
            }
            
            # Обмежуємо значення до [0, 1]
            for key in ["chaos_tolerance", "routine_preference", "decision_speed", 
                       "risk_tendency", "social_communication"]:
                behavior_vector[key] = max(0.0, min(1.0, behavior_vector[key]))
            
            return behavior_vector
            
        except Exception as e:
            # Повертаємо значення за замовчуванням у разі помилки
            return {
                "chaos_tolerance": 0.5,
                "routine_preference": 0.5,
                "decision_speed": 0.5,
                "risk_tendency": 0.5,
                "social_communication": 0.5,
                "emotional_triggers": emotional_trigger,
                "recommended_roles": ["UX/UI Designer", "Data Analyst", "HR Specialist", 
                                     "Backend Developer", "Продакт-менеджер"]
            }

