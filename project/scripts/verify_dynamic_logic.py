import asyncio
import sys
import os

# Додаємо кореневу директорію проекту до PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_engine.behavior_analyzer import BehaviorAnalyzer
from ai_engine.scenario_generator import ScenarioGenerator

async def main():
    analyzer = BehaviorAnalyzer()
    generator = ScenarioGenerator()

    print("--- Тестування BehaviorAnalyzer ---")
    behavior_vector = await analyzer.analyze_survey_responses(
        chaos_vs_routine="люблю хаос",
        deadline_reaction="гнучкість",
        emotional_trigger="багато дрібних правок",
        conflict_reaction="дипломатія",
        social_energy="заряджає",
        team_vs_solo="команда",
        monotony_reaction="втомлює",
        risk_style="ризикую",
        learning_style="практика",
        ideal_day="створюю щось нове з командою"
    )
    print(f"Поведінковий вектор: {behavior_vector}")

    print("\n--- Тестування ScenarioGenerator для нішевої професії (Deep Sea Archaeologist) ---")
    scenario = await generator.generate_scenario("Deep Sea Archaeologist", behavior_vector)
    print(f"Сценарій: {scenario['scenario_description']}")
    print(f"Опції: {[o['text'] for o in scenario['options']]}")

    print("\n--- Тестування ScenarioGenerator для іншої професії (AI Prompt Engineer) ---")
    scenario_2 = await generator.generate_scenario("AI Prompt Engineer", behavior_vector)
    print(f"Сценарій: {scenario_2['scenario_description']}")
    print(f"Опції: {[o['text'] for o in scenario_2['options']]}")

if __name__ == "__main__":
    asyncio.run(main())
