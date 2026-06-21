import json
import sqlite3
from datetime import datetime, timedelta
import os

# Data samples
MOCK_MEMORIES = [
    {
        "memory_id": "mem_001",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=30)).isoformat(),
        "raw_content": "User prefers writing backend logic in Python using FastAPI.",
        "category": "workflow_preference",
        "access_count": 10,
        "last_accessed": (datetime.now() - timedelta(days=1)).isoformat(),
    },
    {
        "memory_id": "mem_002",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=20)).isoformat(),
        "raw_content": "User said they are interested in learning Rust for high-performance microservices.",
        "category": "workflow_preference",
        "access_count": 2,
        "last_accessed": (datetime.now() - timedelta(days=15)).isoformat(),
    },
    {
        "memory_id": "mem_003",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
        "raw_content": "User explicitly stated: 'From now on, I want to use Rust instead of Python for all new backend projects.'",
        "category": "workflow_preference",
        "access_count": 1,
        "last_accessed": datetime.now().isoformat(),
    },
    {
        "memory_id": "mem_004",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=40)).isoformat(),
        "raw_content": "User's favorite color is blue.",
        "category": "entity_fact",
        "access_count": 5,
        "last_accessed": (datetime.now() - timedelta(days=10)).isoformat(),
    },
    {
        "memory_id": "mem_005",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
        "raw_content": "User mentioned they now prefer dark mode and a green aesthetic for their UI.",
        "category": "entity_fact",
        "access_count": 3,
        "last_accessed": datetime.now().isoformat(),
    },
    {
        "memory_id": "mem_006",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
        "raw_content": "User's favorite color is green.",
        "category": "entity_fact",
        "access_count": 1,
        "last_accessed": datetime.now().isoformat(),
    },
]


def generate_json():
    with open("mock_memories.json", "w") as f:
        json.dump(MOCK_MEMORIES, f, indent=4)
    print("Created mock_memories.json")


def generate_sqlite():
    db_path = "mock_memories.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE memories (
            memory_id TEXT PRIMARY KEY,
            user_id TEXT,
            timestamp TEXT,
            raw_content TEXT,
            category TEXT,
            access_count INTEGER,
            last_accessed TEXT,
            extra_data TEXT
        )
    """)

    for mem in MOCK_MEMORIES:
        # Add some mock embedding data for SQLite
        extra_data = json.dumps({"embedding": [0.1, 0.2, 0.3] * 10})
        cursor.execute(
            """
            INSERT INTO memories VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                mem["memory_id"],
                mem["user_id"],
                mem["timestamp"],
                mem["raw_content"],
                mem["category"],
                mem["access_count"],
                mem["last_accessed"],
                extra_data,
            ),
        )

    conn.commit()
    conn.close()
    print("Created mock_memories.db")


if __name__ == "__main__":
    generate_json()
    generate_sqlite()
