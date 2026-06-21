from typing import List, Dict
from src.helpers.pydantic_models import AuditItem, ResolutionAction, MemoryFragment
from datetime import datetime

class MarkdownReporter:
    """
    Generates a structured Markdown report (AUDIT_STAGING.md) for human review.
    Focuses on high-priority contradictions and proposed optimizations.
    """

    def __init__(self, output_path: str = "docs/AUDIT_STAGING.md"):
        self.output_path = output_path

    def generate(self, audit_items: List[AuditItem], all_memories: List[MemoryFragment]):
        """
        Compiles the audit items and original memories into a readable dashboard.
        """
        # Create a lookup for memories by ID
        memory_map = {m.memory_id: m for m in all_memories}

        with open(self.output_path, 'w') as f:
            f.write(f"# 🛡️ Agentic Memory Audit Report\n")
            f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            f.write(f"## 📊 Executive Summary\n")
            hitl_count = sum(1 for item in audit_items if item.action_required == ResolutionAction.HITL_REQUIRED)
            auto_count = sum(1 for item in audit_items if item.action_required != ResolutionAction.HITL_REQUIRED)
            f.write(f"- **Total Issues Found:** {len(audit_items)}\n")
            f.write(f"- **Human-in-the-Loop Required:** {hitl_count}\n")
            f.write(f"- **Automated Optimizations Staged:** {auto_count}\n\n")

            f.write(f"---\n\n")

            if hitl_count > 0:
                f.write(f"## 🚨 HIGH PRIORITY: Human-in-the-Loop Required\n")
                f.write(f"The following items represent logical contradictions or significant preference drift that require manual arbitration.\n\n")

                for item in audit_items:
                    if item.action_required == ResolutionAction.HITL_REQUIRED:
                        self._write_audit_item(f, item, memory_map)

            if auto_count > 0:
                f.write(f"## ⚙️ Automated Optimizations (Staged)\n")
                f.write(f"The following items can be resolved automatically (e.g., redundancy pruning, decay) but are shown here for transparency.\n\n")

                for item in audit_items:
                    if item.action_required != ResolutionAction.HITL_REQUIRED:
                        self._write_audit_item(f, item, memory_map)

        print(f"Audit report generated at {self.output_path}")

    def _write_audit_item(self, f, item: AuditItem, memory_map: Dict[str, MemoryFragment]):
        f.write(f"### 📍 Topic: {item.target_topic}\n")
        f.write(f"- **Cluster ID:** `{item.cluster_id}`\n")
        f.write(f"- **Justification:** {item.justification}\n")
        f.write(f"- **Proposed Action:** `{item.action_required.value.upper()}`\n\n")
        
        f.write(f"#### 💡 Proposal\n")
        f.write(f"> {item.optimized_payload_proposal or 'No specific proposal provided.'}\n\n")

        f.write(f"#### 📄 Underlying Memory Fragments\n")
        f.write(f"| Memory ID | Category | Timestamp | Content |\n")
        f.write(f"| :--- | :--- | :--- | :--- |\n")
        
        for mid in item.affected_memory_ids:
            mem = memory_map.get(mid)
            if mem:
                # Clean up content for table (remove newlines, truncate)
                clean_content = mem.raw_content.replace('\n', ' ')
                f.write(f"| `{mem.memory_id}` | `{mem.category}` | {mem.timestamp.strftime('%Y-%m-%d')} | {clean_content} |\n")
        
        f.write(f"\n---\n\n")
