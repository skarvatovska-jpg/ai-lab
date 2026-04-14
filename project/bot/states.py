"""
FSM стани для бота
"""
from aiogram.fsm.state import State, StatesGroup


class SurveyStates(StatesGroup):
    """Стани для анкети"""
    waiting_chaos_routine = State()
    waiting_deadline = State()
    waiting_emotional_trigger = State()
    waiting_conflict = State()
    waiting_q5 = State()
    waiting_q6 = State()
    waiting_q7 = State()
    waiting_q8 = State()
    waiting_q9 = State()
    waiting_q10 = State()

    # Custom text answer states
    waiting_q1_custom = State()
    waiting_q2_custom = State()
    waiting_q4_custom = State()
    waiting_q5_custom = State()
    waiting_q6_custom = State()
    waiting_q7_custom = State()
    waiting_q8_custom = State()
    waiting_q9_custom = State()


class SimulationStates(StatesGroup):
    """Стани для симуляції"""
    waiting_role_selection = State()
    waiting_custom_role = State()
    waiting_simulation_episode_response = State()
    waiting_custom_episode_response = State()
    simulation_finished = State()
