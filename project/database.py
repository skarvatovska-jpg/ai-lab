"""
Модуль для роботи з базою даних SQLite
"""
import aiosqlite
from typing import Optional, Dict, List, Any
from datetime import datetime
import json
from config import DATABASE_PATH


class Database:
    """Клас для роботи з базою даних"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
    
    async def init_db(self):
        """Ініціалізація бази даних - створення таблиць"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблиця користувачів
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    engagement_level INTEGER DEFAULT 0
                )
            """)
            
            # Таблиця поведінкових векторів (Big5-like)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS behavior_vectors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    chaos_tolerance REAL,
                    routine_preference REAL,
                    decision_speed REAL,
                    risk_tendency REAL,
                    social_communication REAL,
                    emotional_triggers TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Таблиця результатів симуляцій
            await db.execute("""
                CREATE TABLE IF NOT EXISTS simulation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    role_name TEXT,
                    compatibility_score INTEGER,
                    burnout_risk TEXT,
                    strengths TEXT,
                    weaknesses TEXT,
                    recommendations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Таблиця логів LLM запитів
            await db.execute("""
                CREATE TABLE IF NOT EXISTS llm_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    request_type TEXT,
                    prompt TEXT,
                    response TEXT,
                    tokens_used INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            await db.commit()
    
    async def add_user(self, user_id: int, username: Optional[str] = None, first_name: Optional[str] = None):
        """Додати користувача"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR IGNORE INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            """, (user_id, username, first_name))
            await db.commit()
    
    async def save_behavior_vector(
        self,
        user_id: int,
        chaos_tolerance: float,
        routine_preference: float,
        decision_speed: float,
        risk_tendency: float,
        social_communication: float,
        emotional_triggers: str
    ):
        """Зберегти поведінковий вектор користувача"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO behavior_vectors 
                (user_id, chaos_tolerance, routine_preference, decision_speed, 
                 risk_tendency, social_communication, emotional_triggers)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, chaos_tolerance, routine_preference, decision_speed,
                  risk_tendency, social_communication, emotional_triggers))
            await db.commit()
    
    async def get_latest_behavior_vector(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Отримати останній поведінковий вектор користувача"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM behavior_vectors 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None
    
    async def save_simulation_result(
        self,
        user_id: int,
        role_name: str,
        compatibility_score: int,
        burnout_risk: str,
        strengths: str,
        weaknesses: str,
        recommendations: str
    ):
        """Зберегти результат симуляції"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO simulation_results
                (user_id, role_name, compatibility_score, burnout_risk,
                 strengths, weaknesses, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, role_name, compatibility_score, burnout_risk,
                  strengths, weaknesses, recommendations))
            await db.commit()
    
    async def log_llm_request(
        self,
        user_id: int,
        request_type: str,
        prompt: str,
        response: str,
        tokens_used: int = 0
    ):
        """Логувати запит до LLM"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO llm_logs (user_id, request_type, prompt, response, tokens_used)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, request_type, prompt[:10000], response[:10000], tokens_used))
            await db.commit()
    
    async def get_user_simulation_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Отримати історію симуляцій користувача"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM simulation_results 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

