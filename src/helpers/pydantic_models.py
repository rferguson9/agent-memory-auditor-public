from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


# Ingestion Schema (Deterministic Input Contract)
class MemoryFragment(BaseModel):
    memory_id: str
    user_id: str
    timestamp: datetime
    raw_content: str = Field(
        description="The actual string representation of the stored memory."
    )
    category: str = Field(
        description="Context boundary classification (e.g., workflow_preference, entity_fact)."
    )
    access_count: int = 0
    last_accessed: Optional[datetime] = None


# Audit Result Schema (Strict Output Contract)
class ResolutionAction(str, Enum):
    AUTOMATIC_COMPRESS = "automatic_compress"
    AUTOMATIC_DECAY = "automatic_decay"
    HITL_REQUIRED = "hitl_required"


class AuditItem(BaseModel):
    cluster_id: str
    target_topic: str
    action_required: ResolutionAction
    justification: str
    affected_memory_ids: List[str]
    optimized_payload_proposal: Optional[str] = None
