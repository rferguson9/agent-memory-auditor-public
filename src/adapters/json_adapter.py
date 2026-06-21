import json
from typing import List
from src.adapters.base import BaseAdapter
from src.helpers.pydantic_models import MemoryFragment

class JSONAdapter(BaseAdapter):
    """
    Adapter for reading and writing memories stored in a local JSON file.
    Expects a list of memory objects in the JSON file.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def fetch_memories(self) -> List[MemoryFragment]:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError(f"Expected a list of memories in {self.file_path}")
            
            return [MemoryFragment(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading JSON file: {e}")
            return []

    def update_memory(self, memory_id: str, updated_data: dict) -> bool:
        try:
            with open(self.file_path, 'r') as f:
                memories = json.load(f)
            
            updated = False
            for i, mem in enumerate(memories):
                if mem.get('memory_id') == memory_id:
                    memories[i].update(updated_data)
                    updated = True
                    break
            
            if updated:
                with open(self.file_path, 'w') as f:
                    json.dump(memories, f, indent=4, default=str)
                return True
            
            return False
        except Exception as e:
            print(f"Error updating JSON memory: {e}")
            return False

    def delete_memory(self, memory_id: str) -> bool:
        try:
            with open(self.file_path, 'r') as f:
                memories = json.load(f)
            
            initial_len = len(memories)
            memories = [m for m in memories if m.get('memory_id') != memory_id]
            
            if len(memories) < initial_len:
                with open(self.file_path, 'w') as f:
                    json.dump(memories, f, indent=4, default=str)
                return True
            return False
        except Exception as e:
            print(f"Error deleting JSON memory: {e}")
            return False
