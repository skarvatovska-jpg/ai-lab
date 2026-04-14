"""
Модуль для прогнозування ризику вигорання та генерації рекомендацій
"""
import json
from typing import Dict, Any
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL


class BurnoutPredictor:
    """Клас для прогнозування ризику вигорання"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    async def analyze_simulation_response(
        self,
        role_name: str,
        behavior_vector: Dict[str, float],
        scenario_description: str,
        selected_option: str,
        option_text: str
    ) -> Dict[str, Any]:
        """
        Аналізує відповідь користувача в симуляції та генерує прогноз
        
        Returns:
            Dict з полями:
            - compatibility_score: int (0-100)
            - burnout_risk: str ("низький", "середній", "високий")
            - strengths: str (сильні сторони)
            - weaknesses: str (слабкі сторони)
            - recommendations: str (рекомендації)
        """
        
        system_prompt = """Ти експерт з психології праці та кар'єрного консультування. 
Твоя задача - проаналізувати реакцію користувача на професійний сценарій та надати:
1. Оцінку сумісності з роллю (0-100%)
2. Прогноз ризику вигорання (Burnout)
3. Сильні та слабкі сторони
4. Конкретні рекомендації

Важливо:
- Оцінюй не "клінічні симптоми", а патерни поведінки
- Уникай радикальних або ризикованих порад
- Будь конкретним та конструктивним
- Фокусуйся на профілактиці вигорання

Поверни JSON з такими полями:
- compatibility_score: integer (0-100)
- burnout_risk: string ("низький", "середній" або "високий")
- strengths: string (1 коротке речення про головну силу)
- weaknesses: string (1 коротке речення про головний ризик)
- recommendations: string (1-2 дуже короткі поради)

Важливо: поверни ТІЛЬКИ валідний JSON без додаткових пояснень. Пиши максимально стисло. """

        user_prompt = f"""Роль: {role_name}

Поведінковий профіль користувача:
- Толерантність до хаосу: {behavior_vector.get('chaos_tolerance', 0.5):.2f}
- Схильність до рутини: {behavior_vector.get('routine_preference', 0.5):.2f}
- Швидкість прийняття рішень: {behavior_vector.get('decision_speed', 0.5):.2f}
- Схильність до ризику: {behavior_vector.get('risk_tendency', 0.5):.2f}
- Соціальна комунікабельність: {behavior_vector.get('social_communication', 0.5):.2f}
- Емоційні тригери: {behavior_vector.get('emotional_triggers', 'не вказано')}

Сценарій симуляції:
{scenario_description}

Вибір користувача: {option_text}

Проаналізуй сумісність, ризик вигорання та надай рекомендації."""

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
            
            # Валідація та нормалізація
            compatibility = int(result.get("compatibility_score", 50))
            compatibility = max(0, min(100, compatibility))
            
            burnout_risk = result.get("burnout_risk", "середній").lower()
            if burnout_risk not in ["низький", "середній", "високий"]:
                burnout_risk = "середній"
            
            return {
                "compatibility_score": compatibility,
                "burnout_risk": burnout_risk,
                "strengths": result.get("strengths", "Потрібно більше даних для оцінки."),
                "weaknesses": result.get("weaknesses", "Потрібно більше даних для оцінки."),
                "recommendations": result.get("recommendations", "Продовжуйте тестування інших ролей.")
            }
            
        except Exception as e:
            # Повертаємо значення за замовчуванням у разі помилки
            return {
                "compatibility_score": 50,
                "burnout_risk": "середній",
                "strengths": "Потрібно більше даних для детальної оцінки.",
                "weaknesses": "Потрібно більше даних для детальної оцінки.",
                "recommendations": "Спробуйте інші професійні сценарії для повнішої картини."
            }

