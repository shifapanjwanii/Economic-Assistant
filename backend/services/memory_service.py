import aiosqlite
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import config
import os


class MemoryService:
    """Service for managing long-term memory using SQLite"""
    
    def __init__(self):
        self.db_path = config.DATABASE_PATH
        
    async def initialize_database(self):
        """Create database tables if they don't exist"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # User profiles table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    income_range TEXT,
                    debt_level REAL,
                    dependents INTEGER,
                    risk_tolerance TEXT,
                    financial_goals TEXT,
                    preferences TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # Conversation history table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    role TEXT,
                    message TEXT,
                    tools_used TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            """)
            
            # Decisions log table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    query TEXT,
                    recommendation TEXT,
                    acted_upon BOOLEAN,
                    timestamp TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            """)
            
            await db.commit()
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user profile from memory"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM user_profiles WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "user_id": row["user_id"],
                        "income_range": row["income_range"],
                        "debt_level": row["debt_level"],
                        "dependents": row["dependents"],
                        "risk_tolerance": row["risk_tolerance"],
                        "financial_goals": json.loads(row["financial_goals"]) if row["financial_goals"] else {},
                        "preferences": json.loads(row["preferences"]) if row["preferences"] else {},
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    }
        return None
    
    async def create_or_update_user_profile(
        self, 
        user_id: str,
        profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create or update user profile"""
        existing = await self.get_user_profile(user_id)
        timestamp = datetime.now().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            if existing:
                # Update existing profile
                await db.execute("""
                    UPDATE user_profiles
                    SET income_range = ?,
                        debt_level = ?,
                        dependents = ?,
                        risk_tolerance = ?,
                        financial_goals = ?,
                        preferences = ?,
                        updated_at = ?
                    WHERE user_id = ?
                """, (
                    profile_data.get("income_range", existing["income_range"]),
                    profile_data.get("debt_level", existing["debt_level"]),
                    profile_data.get("dependents", existing["dependents"]),
                    profile_data.get("risk_tolerance", existing["risk_tolerance"]),
                    json.dumps(profile_data.get("financial_goals", existing["financial_goals"])),
                    json.dumps(profile_data.get("preferences", existing["preferences"])),
                    timestamp,
                    user_id
                ))
            else:
                # Create new profile
                await db.execute("""
                    INSERT INTO user_profiles (
                        user_id, income_range, debt_level, dependents,
                        risk_tolerance, financial_goals, preferences,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    profile_data.get("income_range"),
                    profile_data.get("debt_level", 0.0),
                    profile_data.get("dependents", 0),
                    profile_data.get("risk_tolerance", "moderate"),
                    json.dumps(profile_data.get("financial_goals", {})),
                    json.dumps(profile_data.get("preferences", {})),
                    timestamp,
                    timestamp
                ))
            
            await db.commit()
        
        return await self.get_user_profile(user_id)
    
    async def add_conversation(
        self,
        user_id: str,
        role: str,
        message: str,
        tools_used: Optional[List[str]] = None
    ):
        """Add a conversation message to history"""
        timestamp = datetime.now().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO conversations (user_id, role, message, tools_used, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                role,
                message,
                json.dumps(tools_used or []),
                timestamp
            ))
            await db.commit()
    
    async def get_conversation_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve recent conversation history"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT role, message, tools_used, timestamp
                FROM conversations
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "role": row["role"],
                        "message": row["message"],
                        "tools_used": json.loads(row["tools_used"]),
                        "timestamp": row["timestamp"]
                    }
                    for row in reversed(rows)  # Reverse to get chronological order
                ]
        
    async def log_decision(
        self,
        user_id: str,
        query: str,
        recommendation: str,
        acted_upon: bool = False
    ):
        """Log a decision made by the agent"""
        timestamp = datetime.now().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO decisions (user_id, query, recommendation, acted_upon, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, query, recommendation, acted_upon, timestamp))
            await db.commit()
    
    async def get_recent_decisions(
        self,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve recent decisions"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT query, recommendation, acted_upon, timestamp
                FROM decisions
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "query": row["query"],
                        "recommendation": row["recommendation"],
                        "acted_upon": bool(row["acted_upon"]),
                        "timestamp": row["timestamp"]
                    }
                    for row in rows
                ]
    
    async def clear_conversation_history(self, user_id: str) -> Dict[str, Any]:
        """Clear all conversation history for a user"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM conversations WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()
        
        return {"success": True, "message": "Conversation history cleared"}
