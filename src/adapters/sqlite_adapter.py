import sqlite3
import json
from typing import List, Optional
from src.adapters.base import BaseAdapter
from src.helpers.pydantic_models import MemoryFragment
from datetime import datetime

class SQLiteAdapter(BaseAdapter):
    """
    Adapter for reading and writing memories stored in a SQLite database.
    Supports basic fields and can store extra data (like embeddings) in a JSON column.
    """

    def __init__(self, db_path: str, table_name: str = "memories"):
        self.db_path = db_path
        self.table_name = table_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    memory_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    timestamp TEXT,
                    raw_content TEXT,
                    category TEXT,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    extra_data TEXT
                )
            """)
            conn.commit()

    def fetch_memories(self, user_id: Optional[str] = None) -> List[MemoryFragment]:
        query = f"SELECT * FROM {self.table_name}"
        params = []
        if user_id:
            query += " WHERE user_id = ?"
            params.append(user_id)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            memories = []
            for row in rows:
                # Convert SQLite row to dictionary and handle timestamp strings
                row_dict = dict(row)
                if row_dict['timestamp']:
                    row_dict['timestamp'] = datetime.fromisoformat(row_dict['timestamp'])
                if row_dict['last_accessed']:
                    row_dict['last_accessed'] = datetime.fromisoformat(row_dict['last_accessed'])
                
                # Remove extra_data before passing to MemoryFragment
                row_dict.pop('extra_data', None)
                memories.append(MemoryFragment(**row_dict))
            return memories

    def update_memory(self, memory_id: str, updated_data: dict) -> bool:
        keys = updated_data.keys()
        set_clause = ", ".join([f"{k} = ?" for k in keys])
        values = list(updated_data.values())
        values.append(memory_id)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"UPDATE {self.table_name} SET {set_clause} WHERE memory_id = ?", values)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating SQLite memory: {e}")
            return False

    def delete_memory(self, memory_id: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM {self.table_name} WHERE memory_id = ?", (memory_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting SQLite memory: {e}")
            return False
