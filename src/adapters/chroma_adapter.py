from typing import List, Optional
from datetime import datetime
import chromadb
from src.adapters.base import BaseAdapter
from src.helpers.pydantic_models import MemoryFragment

class ChromaAdapter(BaseAdapter):
    """
    Adapter for ChromaDB.
    Maps a collection's documents and metadata to MemoryFragments.
    """

    def __init__(self, path: str, collection_name: str = "memories"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def fetch_memories(self, user_id: Optional[str] = None) -> List[MemoryFragment]:
        where = {"user_id": user_id} if user_id else None
        results = self.collection.get(where=where)
        
        memories = []
        # results is a dict with keys: ids, documents, metadatas, etc.
        for i in range(len(results['ids'])):
            metadata = results['metadatas'][i] or {}
            memories.append(MemoryFragment(
                memory_id=results['ids'][i],
                user_id=metadata.get('user_id', 'unknown'),
                timestamp=datetime.fromisoformat(metadata.get('timestamp', datetime.now().isoformat())),
                raw_content=results['documents'][i],
                category=metadata.get('category', 'general'),
                access_count=metadata.get('access_count', 0),
                last_accessed=datetime.fromisoformat(metadata.get('last_accessed', datetime.now().isoformat()))
            ))
        return memories

    def update_memory(self, memory_id: str, updated_data: dict) -> bool:
        try:
            # Prepare update
            update_kwargs = {"ids": [memory_id]}
            if 'raw_content' in updated_data:
                update_kwargs["documents"] = [updated_data['raw_content']]
            
            # Filter metadata updates
            meta_updates = {k: v for k, v in updated_data.items() if k != 'raw_content'}
            if meta_updates:
                # We need to get existing metadata to merge
                existing = self.collection.get(ids=[memory_id])
                if existing['metadatas']:
                    current_meta = existing['metadatas'][0]
                    current_meta.update(meta_updates)
                    update_kwargs["metadatas"] = [current_meta]

            self.collection.update(**update_kwargs)
            return True
        except Exception as e:
            print(f"Error updating ChromaDB: {e}")
            return False

    def delete_memory(self, memory_id: str) -> bool:
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception as e:
            print(f"Error deleting ChromaDB memory: {e}")
            return False
