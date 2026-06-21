from typing import List, Optional
from datetime import datetime
from src.adapters.base import BaseAdapter
from src.helpers.pydantic_models import MemoryFragment

class LangGraphAdapter(BaseAdapter):
    """
    Adapter for LangGraph BaseStore.
    Allows auditing long-term memories stored in LangGraph.
    """

    def __init__(self, store, namespace: List[str] = ("memories",)):
        self.store = store
        self.namespace = namespace

    def fetch_memories(self) -> List[MemoryFragment]:
        # LangGraph list returns List[Item]
        items = self.store.list(self.namespace)
        
        memories = []
        for item in items:
            # item.value is usually a dict
            val = item.value
            metadata = item.metadata or {}
            
            memories.append(MemoryFragment(
                memory_id=item.key,
                user_id=metadata.get('user_id', 'unknown'),
                timestamp=datetime.fromisoformat(metadata.get('created_at', datetime.now().isoformat())),
                raw_content=val.get('content', str(val)),
                category=metadata.get('category', 'general'),
                access_count=metadata.get('access_count', 0),
                last_accessed=datetime.fromisoformat(metadata.get('updated_at', datetime.now().isoformat()))
            ))
        return memories

    def update_memory(self, memory_id: str, updated_data: dict) -> bool:
        try:
            # LangGraph put requires a dict value
            # We fetch existing to preserve metadata
            existing = self.store.get(self.namespace, memory_id)
            new_value = existing.value if existing else {}
            new_value['content'] = updated_data.get('raw_content', new_value.get('content'))
            
            self.store.put(self.namespace, memory_id, new_value)
            return True
        except Exception as e:
            print(f"Error updating LangGraph Store: {e}")
            return False

    def delete_memory(self, memory_id: str) -> bool:
        try:
            self.store.delete(self.namespace, memory_id)
            return True
        except Exception as e:
            print(f"Error deleting LangGraph Store memory: {e}")
            return False
