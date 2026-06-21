import json
from typing import List, Optional
from datetime import datetime
from src.adapters.base import BaseAdapter
from src.helpers.pydantic_models import MemoryFragment

try:
    from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart
    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False
    class ModelMessage: pass
    class ModelRequest: pass
    class ModelResponse: pass
    class TextPart: pass

class PydanticAIAdapter(BaseAdapter):
    """
    Adapter for PydanticAI (pydantic-ai) agent conversation histories.
    Ingests ModelMessage lists or deserializes them from JSON logs to sanitize, audit, and compress state.
    """

    def __init__(self, source: Optional[str] = None, messages: Optional[List[ModelMessage]] = None, user_id: str = "default_user"):
        if not PYDANTIC_AI_AVAILABLE:
            raise ImportError(
                "PydanticAI is not installed. Please run 'pip install pydantic-ai'."
            )
        self.source = source
        self.messages = messages or []
        self.user_id = user_id

    def fetch_memories(self) -> List[MemoryFragment]:
        raw_messages = []
        
        # 1. Load messages from serialized JSON source if provided
        if self.source:
            try:
                with open(self.source, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    for idx, item in enumerate(data):
                        # Extract text from ModelRequest/ModelResponse structured parts
                        parts = item.get('parts', [])
                        text_content = ""
                        for part in parts:
                            if isinstance(part, dict):
                                text_content += part.get('text', part.get('content', ''))
                            elif hasattr(part, 'text'):
                                text_content += part.text
                        
                        if text_content.strip():
                            raw_messages.append((
                                idx, 
                                text_content, 
                                item.get('timestamp') or datetime.now().isoformat()
                            ))
            except Exception as e:
                print(f"Error reading PydanticAI messages from source: {e}")
                
        # 2. Map direct PydanticAI message objects if passed in SDK format
        for idx, msg in enumerate(self.messages):
            text_content = ""
            # Handle request parts
            if hasattr(msg, 'parts'):
                for part in msg.parts:
                    # In PydanticAI, text content can be stored in 'content' or 'text' properties
                    if hasattr(part, 'content'):
                        text_content += str(part.content)
                    elif hasattr(part, 'text'):
                        text_content += str(part.text)
                        
            if text_content.strip():
                # Extract timestamp if available on msg
                ts = getattr(msg, 'timestamp', None) or datetime.now().isoformat()
                if isinstance(ts, datetime):
                    ts = ts.isoformat()
                raw_messages.append((idx, text_content, ts))

        # Convert to unified MemoryFragment schemas
        memories = []
        for i, text, ts in raw_messages:
            memories.append(MemoryFragment(
                memory_id=f"pydantic_ai_{i:04d}",
                user_id=self.user_id,
                timestamp=datetime.fromisoformat(ts),
                raw_content=text.strip(),
                category="conversation_history",
                access_count=1,
                last_accessed=datetime.fromisoformat(ts)
            ))
            
        return memories

    def update_memory(self, memory_id: str, updated_data: dict) -> bool:
        # PydanticAI conversation histories are immutable audit trails. 
        # For the active sync simulation, we flag updates or log them to Logfire.
        print(f"Updating PydanticAI memory fragment: {memory_id} -> {updated_data.get('raw_content', '')[:30]}...")
        return True

    def delete_memory(self, memory_id: str) -> bool:
        # In a production DB setting, this would drop or archive the message node
        print(f"Deleting PydanticAI memory node: {memory_id}")
        return True
