from src.adapters.json_adapter import JSONAdapter
from src.adapters.sqlite_adapter import SQLiteAdapter
from src.adapters.postgres_adapter import PostgresAdapter
from src.adapters.mem0_adapter import Mem0Adapter
from src.adapters.langgraph_adapter import LangGraphAdapter
from src.adapters.chroma_adapter import ChromaAdapter
from src.adapters.pydantic_ai_adapter import PydanticAIAdapter

def get_adapter(adapter_type: str, source: str):
    """
    Factory function to return the correct adapter based on type.
    'source' is interpreted differently based on the adapter.
    """
    t = adapter_type.lower()
    
    if t == "json":
        return JSONAdapter(source)
    elif t == "sqlite":
        return SQLiteAdapter(source)
    elif t == "postgres":
        # Assumes source is a connection string
        return PostgresAdapter(source)
    elif t == "mem0":
        # Assumes source is user_id (API key should be in .env)
        return Mem0Adapter(user_id=source)
    elif t == "chroma":
        # Assumes source is path to persistent storage
        return ChromaAdapter(path=source)
    elif t == "pydantic_ai":
        # Assumes source is a path to serialized ModelMessage JSON log
        return PydanticAIAdapter(source=source)
    elif t == "langgraph":
        # For LangGraph, we'd typically need the actual store object.
        # As a CLI tool, this is tricky, but we can assume source is a connection 
        # string to a LangGraph-compatible DB if we implement a lazy-loader.
        # For now, we'll raise an error if called from CLI without proper setup.
        raise ValueError("LangGraphAdapter requires direct object passing; CLI support coming soon.")
    else:
        raise ValueError(f"Unknown adapter type: {adapter_type}")
