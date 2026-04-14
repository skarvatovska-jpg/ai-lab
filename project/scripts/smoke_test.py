import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

try:
    from bot.handlers import router as main_router
    print("✓ bot.handlers imported")
    from bot.twin_survey import router as twin_survey_router
    print("✓ bot.twin_survey imported")
    from ai_engine.behavior_analyzer import BehaviorAnalyzer
    print("✓ ai_engine.behavior_analyzer imported")
    from ai_engine.scenario_generator import ScenarioGenerator
    print("✓ ai_engine.scenario_generator imported")
    from database import Database
    print("✓ database imported")
    from config import BOT_TOKEN
    print("✓ config imported")
    print("\nSUCCESS: All core modules imported correctly.")
except Exception as e:
    print(f"\nFAILURE: Import error: {e}")
    sys.exit(1)
