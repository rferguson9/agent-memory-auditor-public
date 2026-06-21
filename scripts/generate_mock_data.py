import json
import sqlite3
from datetime import datetime, timedelta
import os

# Complex Mock Data Samples
MOCK_MEMORIES = [
    # --- Scenario 1: Programming Language Preference (Contradiction) ---
    {
        "memory_id": "mem_001",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=60)).isoformat(),
        "raw_content": "User prefers writing backend logic in Python using FastAPI.",
        "category": "workflow_preference",
        "access_count": 15,
        "last_accessed": (datetime.now() - timedelta(days=20)).isoformat()
    },
    {
        "memory_id": "mem_002",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=45)).isoformat(),
        "raw_content": "User mentioned they are interested in learning Rust for high-performance microservices.",
        "category": "workflow_preference",
        "access_count": 5,
        "last_accessed": (datetime.now() - timedelta(days=30)).isoformat()
    },
    {
        "memory_id": "mem_003",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
        "raw_content": "User explicitly stated: 'From now on, I want to use Rust instead of Python for all new backend projects.'",
        "category": "workflow_preference",
        "access_count": 2,
        "last_accessed": datetime.now().isoformat()
    },

    # --- Scenario 2: User Aesthetic / Favorite Color (Contradiction) ---
    {
        "memory_id": "mem_004",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=90)).isoformat(),
        "raw_content": "User's favorite color is blue.",
        "category": "entity_fact",
        "access_count": 20,
        "last_accessed": (datetime.now() - timedelta(days=40)).isoformat()
    },
    {
        "memory_id": "mem_005",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=10)).isoformat(),
        "raw_content": "User mentioned they now prefer dark mode and a green aesthetic for their UI.",
        "category": "entity_fact",
        "access_count": 8,
        "last_accessed": (datetime.now() - timedelta(days=1)).isoformat()
    },
    {
        "memory_id": "mem_006",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
        "raw_content": "User's favorite color is green.",
        "category": "entity_fact",
        "access_count": 3,
        "last_accessed": datetime.now().isoformat()
    },

    # --- Scenario 3: Dev Environment Setup (Compression) ---
    {
        "memory_id": "mem_007",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=15)).isoformat(),
        "raw_content": "The user prefers to have a very specific setup for their development environment. They like to use a dark theme with high contrast.",
        "category": "dev_env",
        "access_count": 4,
        "last_accessed": (datetime.now() - timedelta(days=5)).isoformat()
    },
    {
        "memory_id": "mem_008",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=14)).isoformat(),
        "raw_content": "The user find it helpful to have a large font size for better readability.",
        "category": "dev_env",
        "access_count": 3,
        "last_accessed": (datetime.now() - timedelta(days=5)).isoformat()
    },
    {
        "memory_id": "mem_009",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=12)).isoformat(),
        "raw_content": "User prefers using JetBrains Mono typeface for all their coding tasks.",
        "category": "dev_env",
        "access_count": 5,
        "last_accessed": (datetime.now() - timedelta(days=5)).isoformat()
    },
    {
        "memory_id": "mem_010",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=10)).isoformat(),
        "raw_content": "The user is quite adamant about their font choice; JetBrains Mono is their absolute favorite.",
        "category": "dev_env",
        "access_count": 2,
        "last_accessed": (datetime.now() - timedelta(days=5)).isoformat()
    },

    # --- Scenario 4: Work Habits (Nuanced Contradiction) ---
    {
        "memory_id": "mem_011",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=30)).isoformat(),
        "raw_content": "User likes to start their work day early, usually around 8 AM.",
        "category": "work_habits",
        "access_count": 10,
        "last_accessed": (datetime.now() - timedelta(days=10)).isoformat()
    },
    {
        "memory_id": "mem_012",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=15)).isoformat(),
        "raw_content": "User mentioned they are actually most productive late at night, often starting deep work sessions around 9 PM.",
        "category": "work_habits",
        "access_count": 5,
        "last_accessed": (datetime.now() - timedelta(days=2)).isoformat()
    },
    {
        "memory_id": "mem_013",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=3)).isoformat(),
        "raw_content": "User requested to schedule all meetings for early morning hours, specifically before 10 AM, to free up their afternoon.",
        "category": "work_habits",
        "access_count": 2,
        "last_accessed": datetime.now().isoformat()
    },

    # --- Scenario 5: Cloud Infrastructure (Complex Compression) ---
    {
        "memory_id": "mem_014",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=40)).isoformat(),
        "raw_content": "User is currently leveraging Amazon Web Services (AWS) for their primary project deployment.",
        "category": "infrastructure",
        "access_count": 12,
        "last_accessed": (datetime.now() - timedelta(days=10)).isoformat()
    },
    {
        "memory_id": "mem_015",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=38)).isoformat(),
        "raw_content": "User mentioned they have several S3 buckets configured for static asset storage on AWS.",
        "category": "infrastructure",
        "access_count": 8,
        "last_accessed": (datetime.now() - timedelta(days=10)).isoformat()
    },
    {
        "memory_id": "mem_016",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=35)).isoformat(),
        "raw_content": "The application's backend is running on an AWS EC2 instance. The instance type is t3.medium.",
        "category": "infrastructure",
        "access_count": 10,
        "last_accessed": (datetime.now() - timedelta(days=10)).isoformat()
    },
    {
        "memory_id": "mem_017",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=30)).isoformat(),
        "raw_content": "User explicitly noted that they prefer AWS over Google Cloud Platform (GCP) or Azure due to their familiarity with the AWS console interface.",
        "category": "infrastructure",
        "access_count": 6,
        "last_accessed": (datetime.now() - timedelta(days=10)).isoformat()
    },

    # --- Scenario 6: Dietary Choices (Strong Contradiction) ---
    {
        "memory_id": "mem_018",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=100)).isoformat(),
        "raw_content": "User identified as a strict lifelong vegetarian during a discussion about lunch options.",
        "category": "personal_info",
        "access_count": 18,
        "last_accessed": (datetime.now() - timedelta(days=50)).isoformat()
    },
    {
        "memory_id": "mem_019",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
        "raw_content": "The user raved about a medium-rare ribeye steak they had last night, saying it was the best meal they've had in years.",
        "category": "personal_info",
        "access_count": 2,
        "last_accessed": datetime.now().isoformat()
    },

    # --- Scenario 7: Tooling (Redundant Compression) ---
    {
        "memory_id": "mem_020",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=20)).isoformat(),
        "raw_content": "User utilizes Visual Studio Code as their primary IDE.",
        "category": "tooling",
        "access_count": 10,
        "last_accessed": (datetime.now() - timedelta(days=5)).isoformat()
    },
    {
        "memory_id": "mem_021",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=18)).isoformat(),
        "raw_content": "VS Code is the main code editor the user has open every day.",
        "category": "tooling",
        "access_count": 8,
        "last_accessed": (datetime.now() - timedelta(days=5)).isoformat()
    },
    {
        "memory_id": "mem_022",
        "user_id": "user_123",
        "timestamp": (datetime.now() - timedelta(days=15)).isoformat(),
        "raw_content": "User has installed several important extensions in VS Code, including the Python and Pydantic plugins.",
        "category": "tooling",
        "access_count": 12,
        "last_accessed": (datetime.now() - timedelta(days=5)).isoformat()
    }
]

def generate_json():
    os.makedirs('data', exist_ok=True)
    with open('data/mock_memories.json', 'w') as f:
        json.dump(MOCK_MEMORIES, f, indent=4)
    print("Created data/mock_memories.json")

def generate_sqlite():
    os.makedirs('data', exist_ok=True)
    db_path = 'data/mock_memories.db'
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
        extra_data = json.dumps({"embedding": [0.1, 0.2, 0.3] * 10})
        cursor.execute("""
            INSERT INTO memories VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mem['memory_id'],
            mem['user_id'],
            mem['timestamp'],
            mem['raw_content'],
            mem['category'],
            mem['access_count'],
            mem['last_accessed'],
            extra_data
        ))
    
    conn.commit()
    conn.close()
    print("Created data/mock_memories.db")

if __name__ == "__main__":
    generate_json()
    generate_sqlite()
