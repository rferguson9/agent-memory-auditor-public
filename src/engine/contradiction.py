from typing import List, Optional
from src.helpers.pydantic_models import MemoryFragment, AuditItem, ResolutionAction
from src.engine.llm_provider import BaseLLMProvider

class ContradictionEngine:
    """
    Analyzes a cluster of memories for logical contradictions or redundancy using an LLM.
    """

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def analyze_cluster(self, cluster_id: str, memories: List[MemoryFragment]) -> Optional[AuditItem]:
        if not memories:
            return None

        fragment_text = "\n".join([
            f"ID: {m.memory_id} | Content: {m.raw_content}" 
            for m in memories
        ])

        prompt = f"""
        You are the Agentic Memory Auditor (AMA). Your task is to analyze a cluster of memory fragments 
        and identify if there are logical contradictions, structural redundancies, or shifts in user preference.

        MEMORY CLUSTER:
        {fragment_text}

        DIRECTIONS:
        1. If the memories contain contradictory facts or a clear shift in human preference, 
           set action_required to 'hitl_required'. The 'optimized_payload_proposal' should be an inquiry for a human.
        2. If the memories contain Sensitive PII (Passwords, SSNs, credit cards, or exact home addresses) that the agent shouldn't store long-term,
           set action_required to 'hitl_required'. The 'justification' should flag this as a Privacy Violation.
        3. If the memories are just wordy/redundant, set action_required to 'automatic_compress'. The 'optimized_payload_proposal' should be a single, dense JSON-like string.
        4. If a cluster contains memories that are extremely old, low-access, and no longer relevant (Temporal Decay), 
           set action_required to 'automatic_decay'.
        5. If there are no issues, return null.

        Output MUST be a JSON object matching this schema:
        {{
            "cluster_id": "{cluster_id}",
            "target_topic": "string",
            "action_required": "hitl_required" | "automatic_compress" | "automatic_decay",
            "justification": "string",
            "affected_memory_ids": ["string"],
            "optimized_payload_proposal": "string"
        }}
        """

        try:
            data = self.provider.generate_json(prompt)
            if not data or data.get("action_required") is None:
                return None
                
            return AuditItem(**data)
        except Exception as e:
            print(f"Audit Analysis Error/No issue: {e}")
            return None
