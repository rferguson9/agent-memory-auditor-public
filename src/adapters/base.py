from abc import ABC, abstractmethod
from typing import List
from src.helpers.pydantic_models import MemoryFragment

class BaseAdapter(ABC):
    """
    Abstract Base Class for all Memory Adapters.
    Ensures that any data source (SQL, JSON, Vector) is translated into
    the deterministic MemoryFragment schema.
    """

    @abstractmethod
    def fetch_memories(self, **kwargs) -> List[MemoryFragment]:
        """
        Fetches raw memory data from the source and converts it into
        a list of MemoryFragment objects.
        """
        pass

    @abstractmethod
    def update_memory(self, memory_id: str, updated_data: dict) -> bool:
        """
        Updates a specific memory in the source database.
        Used for automated pruning or optimization syncs.
        """
        pass

    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        """
        Deletes a specific memory from the source database.
        """
        pass
