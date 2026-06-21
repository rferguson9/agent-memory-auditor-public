from typing import List
from src.adapters.base import BaseAdapter
from src.helpers.pydantic_models import AuditItem, ResolutionAction

class ExecutionHandler:
    """
    Closes the state sync loop by applying audit resolutions to the underlying store.
    """

    def __init__(self, adapter: BaseAdapter, redundancy_action: str = "archive"):
        self.adapter = adapter
        self.redundancy_action = redundancy_action.lower()

    def execute_batch(self, audit_items: List[AuditItem]) -> dict:
        results = {"processed": 0, "errors": 0, "actions": {}}
        
        for item in audit_items:
            action = item.action_required
            
            if action == ResolutionAction.AUTOMATIC_COMPRESS:
                # Apply compression sync
                success = self._handle_compression(item)
                if success:
                    results["processed"] += 1
                    results["actions"]["compress"] = results["actions"].get("compress", 0) + 1
                else:
                    results["errors"] += 1

            elif action == ResolutionAction.AUTOMATIC_DECAY:
                # Apply decay (e.g., lower access count or delete)
                success = self._handle_decay(item)
                if success:
                    results["processed"] += 1
                    results["actions"]["decay"] = results["actions"].get("decay", 0) + 1
                else:
                    results["errors"] += 1
            
            # HITL items are skipped by the automated execution handler 
            # as they require external approval via the staging dashboard.
            
        return results

    def _handle_compression(self, item: AuditItem) -> bool:
        """
        Updates the target store with the optimized payload.
        Updates the first memory in the list and either physically deletes or archives the rest.
        """
        if not item.optimized_payload_proposal:
            return False
        if not item.affected_memory_ids:
            return False
            
        # 1. Update the first memory with the compressed payload
        primary_id = item.affected_memory_ids[0]
        success = self.adapter.update_memory(primary_id, {
            "raw_content": item.optimized_payload_proposal,
            "category": f"{item.cluster_id}_optimized"
        })
        
        if not success:
            return False
            
        # 2. Prune (delete or archive) the secondary redundant memory fragments
        secondary_ids = item.affected_memory_ids[1:]
        for mid in secondary_ids:
            if self.redundancy_action == "delete":
                print(f"🗑️ Deleting redundant memory: {mid}")
                self.adapter.delete_memory(mid)
            else:
                print(f"📦 Archiving redundant memory: {mid}")
                self.adapter.update_memory(mid, {
                    "category": f"archived_{item.cluster_id}"
                })
                
        return True

    def _handle_decay(self, item: AuditItem) -> bool:
        # Implementation for temporal decay
        for mid in item.affected_memory_ids:
            self.adapter.update_memory(mid, {"access_count": 0})
        return True
