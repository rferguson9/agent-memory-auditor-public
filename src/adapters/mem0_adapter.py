from typing import List, Optional
from datetime import datetime
from src.adapters.base import BaseAdapter
from src.helpers.pydantic_models import MemoryFragment

class Mem0Adapter(BaseAdapter):
    """
    Adapter for Mem0 (mem0ai).
    Connects to either Cloud or Open Source version.
    """

    def __init__(self, api_key: Optional[str] = None, user_id: str = "default_user"):
        from mem0 import Memory
        self.user_id = user_id
        # If no API key, assumes local/open-source mode
        if api_key:
            from mem0 import MemoryClient
            self.client = MemoryClient(api_key=api_key)
            self.is_cloud = True
        else:
            self.client = Memory()
            self.is_cloud = False

    def fetch_memories(self) -> List[MemoryFragment]:
        # Mem0 v3 uses filters dict
        results = self.client.get_all(filters={"user_id": self.user_id})
        
        # Cloud returns a dict with 'results', Local returns a list
        mem_list = results.get('results', []) if self.is_cloud else results
        
        memories = []
        for m in mem_list:
            # Map Mem0 schema to MemoryFragment
            # Mem0 usually has: id, memory, metadata, created_at
            metadata = m.get('metadata', {})
            memories.append(MemoryFragment(
                memory_id=m['id'],
                user_id=metadata.get('user_id', self.user_id),
                timestamp=datetime.fromisoformat(m['created_at'].replace('Z', '+00:00')),
                raw_content=m['memory'],
                category=metadata.get('category', 'general'),
                access_count=metadata.get('access_count', 0),
                last_accessed=datetime.fromisoformat(m.get('updated_at', m['created_at']).replace('Z', '+00:00'))
            ))
        return memories

    def update_memory(self, memory_id: str, updated_data: dict) -> bool:
        # Mem0 doesn't have a direct 'update' in the same sense as SQL,
        # but we can update metadata or re-add.
        # For the prototype, we use the 'update' method if available.
        try:
            self.client.update(memory_id, data=updated_data.get('raw_content', ""))
            return True
        except Exception as e:
            print(f"Error updating Mem0: {e}")
            return False

    def delete_memory(self, memory_id: str) -> bool:
        try:
            self.client.delete(memory_id)
            return True
        except Exception as e:
            print(f"Error deleting Mem0 memory: {e}")
            return False
