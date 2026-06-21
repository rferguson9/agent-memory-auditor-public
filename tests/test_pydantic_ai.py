import os
import json
import tempfile
from datetime import datetime
from src.adapters.pydantic_ai_adapter import PydanticAIAdapter, PYDANTIC_AI_AVAILABLE

try:
    from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, ModelResponsePart
except ImportError:
    class ModelRequest: pass
    class ModelResponse: pass
    class TextPart: pass

def test_pydantic_ai_json_deserialization():
    if not PYDANTIC_AI_AVAILABLE:
        # Skip if pydantic-ai is not installed locally
        return

    # Create temporary JSON representing a serialized PydanticAI message history
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        temp_path = f.name

    mock_history = [
        {
            "parts": [
                {"text": "User wants to write an econometric time-series forecast in Rust."}
            ],
            "timestamp": datetime.now().isoformat()
        },
        {
            "parts": [
                {"content": "Agent replies: Sure, let's build a vector autoregression model!"}
            ],
            "timestamp": datetime.now().isoformat()
        }
    ]

    with open(temp_path, "w") as f:
        json.dump(mock_history, f)

    try:
        adapter = PydanticAIAdapter(source=temp_path)
        memories = adapter.fetch_memories()
        
        assert len(memories) == 2
        assert memories[0].raw_content == "User wants to write an econometric time-series forecast in Rust."
        assert memories[0].category == "conversation_history"
        assert memories[1].raw_content == "Agent replies: Sure, let's build a vector autoregression model!"
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
