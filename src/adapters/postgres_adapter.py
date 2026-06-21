import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import psycopg
from pgvector.psycopg import register_vector
from src.adapters.base import BaseAdapter
from src.helpers.pydantic_models import MemoryFragment

class PostgresAdapter(BaseAdapter):
    """
    Adapter for PostgreSQL with pgvector support.
    Expected table schema:
    CREATE TABLE memories (
        memory_id TEXT PRIMARY KEY,
        user_id TEXT,
        timestamp TIMESTAMPTZ,
        raw_content TEXT,
        category TEXT,
        access_count INTEGER DEFAULT 0,
        last_accessed TIMESTAMPTZ,
        embedding vector(1536) -- Optional
    );
    """

    def __init__(self, connection_string: str, table_name: str = "memories"):
        self.conn_str = connection_string
        self.table_name = table_name

    def fetch_memories(self, user_id: Optional[str] = None) -> List[MemoryFragment]:
        query = f"SELECT * FROM {self.table_name}"
        params = []
        if user_id:
            query += " WHERE user_id = %s"
            params.append(user_id)

        memories = []
        with psycopg.connect(self.conn_str) as conn:
            register_vector(conn)
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
                for row in rows:
                    # Clean row for Pydantic (remove embedding)
                    row.pop('embedding', None)
                    memories.append(MemoryFragment(**row))
        return memories

    def update_memory(self, memory_id: str, updated_data: dict) -> bool:
        set_clause = ", ".join([f"{k} = %s" for k in updated_data.keys()])
        values = list(updated_data.values())
        values.append(memory_id)

        try:
            with psycopg.connect(self.conn_str) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"UPDATE {self.table_name} SET {set_clause} WHERE memory_id = %s",
                        values
                    )
                    conn.commit()
                    return cur.rowcount > 0
        except Exception as e:
            print(f"Error updating Postgres memory: {e}")
            return False

    def delete_memory(self, memory_id: str) -> bool:
        try:
            with psycopg.connect(self.conn_str) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"DELETE FROM {self.table_name} WHERE memory_id = %s",
                        (memory_id,)
                    )
                    conn.commit()
                    return cur.rowcount > 0
        except Exception as e:
            print(f"Error deleting Postgres memory: {e}")
            return False
