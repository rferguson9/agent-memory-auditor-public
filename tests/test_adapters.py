from src.adapters.json_adapter import JSONAdapter
from src.adapters.sqlite_adapter import SQLiteAdapter
import os

def test_json_adapter():
    print("Testing JSON Adapter...")
    adapter = JSONAdapter('mock_memories.json')
    memories = adapter.fetch_memories()
    print(f"Fetched {len(memories)} memories from JSON.")
    for mem in memories:
        print(f" - [{mem.category}] {mem.raw_content[:50]}...")
    print("-" * 20)

def test_sqlite_adapter():
    print("Testing SQLite Adapter...")
    adapter = SQLiteAdapter('mock_memories.db')
    memories = adapter.fetch_memories()
    print(f"Fetched {len(memories)} memories from SQLite.")
    for mem in memories:
        print(f" - [{mem.category}] {mem.raw_content[:50]}...")
    print("-" * 20)

if __name__ == "__main__":
    test_json_adapter()
    test_sqlite_adapter()
