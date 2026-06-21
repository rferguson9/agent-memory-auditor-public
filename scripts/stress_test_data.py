import json
import sqlite3
import random
import os
from datetime import datetime, timedelta

# Stress Test Configuration
NUM_MEMORIES = 120
CATEGORIES = ["workflow", "personal", "travel", "coding", "finance", "health"]
TOPICS = {
    "workflow": ["agile", "standups", "jira", "sprints", "hiring"],
    "personal": ["hobbies", "family", "pets", "food", "preferences"],
    "travel": ["flights", "hotels", "destinations", "itinerary", "packing"],
    "coding": ["python", "rust", "javascript", "testing", "debugging"],
    "finance": ["budgeting", "investing", "taxes", "banking", "crypto"],
    "health": ["exercise", "diet", "sleep", "doctors", "vitamins"]
}

def generate_random_memory(idx):
    cat = random.choice(CATEGORIES)
    topic = random.choice(TOPICS[cat])
    days_ago = random.randint(1, 180)
    access_count = random.randint(0, 50)
    
    # Intentionally create some "messy" data
    if idx % 10 == 0:
        content = f"User explicitly said they LOVE {topic} now."
    elif idx % 15 == 0:
        content = f"User is bored of {topic} and wants to stop."
    else:
        content = f"User mentioned {topic} during a conversation about {cat}. They seemed interested in learning more."

    # Add a PII risk
    if idx == 50:
        content = "User password for the internal dashboard is: SuperSecret123!"
        cat = "security_risk"

    return {
        "memory_id": f"stress_{idx:04d}",
        "user_id": "user_stress_test",
        "timestamp": (datetime.now() - timedelta(days=days_ago)).isoformat(),
        "raw_content": content,
        "category": cat,
        "access_count": access_count,
        "last_accessed": (datetime.now() - timedelta(days=random.randint(0, days_ago))).isoformat()
    }

def generate_stress_data():
    os.makedirs('data', exist_ok=True)
    db_path = 'data/stress_test.db'
    
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
    
    print(f"Generating {NUM_MEMORIES} stress test memories...")
    for i in range(NUM_MEMORIES):
        mem = generate_random_memory(i)
        extra_data = json.dumps({"stress_index": i})
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
    print(f"✅ Created {db_path}")

if __name__ == "__main__":
    generate_stress_data()
