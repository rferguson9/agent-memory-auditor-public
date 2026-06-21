import os
import json
from typing import List, Dict
from dbos import DBOS, DBOSConfig
from src.adapters.factory import get_adapter
from src.engine.clustering import ClusteringEngine
from src.engine.contradiction import ContradictionEngine
from src.engine.execution import ExecutionHandler
from src.engine.llm_provider import get_llm_provider
from src.helpers.pydantic_models import MemoryFragment, AuditItem, ResolutionAction
from src.reporter.markdown_reporter import MarkdownReporter

# Optional Pydantic Logfire Tracing Integration
try:
    import logfire
except ImportError:
    logfire = None

# Configure DBOS
config: DBOSConfig = {
    "name": "ama-auditor",
    "system_database_url": "sqlite:///data/dbos_system.db",
}
DBOS(config=config)

# Initialize clustering engine (non-LLM)
clustering_engine = ClusteringEngine()
reporter = MarkdownReporter()

@DBOS.step()
def fetch_memories_step(adapter_type: str, source: str) -> List[dict]:
    """Step 1: Fetch raw memories from the source."""
    print(f"Fetching memories from {source} ({adapter_type})...")
    if logfire:
        with logfire.span("fetch_memories_step", adapter_type=adapter_type, source=source):
            adapter = get_adapter(adapter_type, source)
            memories = adapter.fetch_memories()
    else:
        adapter = get_adapter(adapter_type, source)
        memories = adapter.fetch_memories()
        
    return [m.model_dump(mode='json') for m in memories]

@DBOS.step()
def cluster_memories_step(memories_data: List[dict]) -> Dict[str, List[dict]]:
    """Step 2: Group memories into topical clusters."""
    print(f"Clustering {len(memories_data)} memories...")
    if logfire:
        with logfire.span("cluster_memories_step", count=len(memories_data)):
            memories = [MemoryFragment(**m) for m in memories_data]
            clusters = clustering_engine.cluster(memories)
    else:
        memories = [MemoryFragment(**m) for m in memories_data]
        clusters = clustering_engine.cluster(memories)
        
    return {k: [m.model_dump(mode='json') for m in v] for k, v in clusters.items()}

@DBOS.step()
def analyze_clusters_step(clusters_data: Dict[str, List[dict]], llm_provider: str, llm_model: str) -> List[dict]:
    """Step 3: Analyze each cluster for contradictions or redundancy."""
    print(f"Analyzing {len(clusters_data)} clusters using {llm_provider} ({llm_model})...")
    if logfire:
        with logfire.span("analyze_clusters_step", provider=llm_provider, model=llm_model):
            provider = get_llm_provider(llm_provider, llm_model)
            engine = ContradictionEngine(provider)
            audit_results = []
            for cluster_id, items_data in clusters_data.items():
                items = [MemoryFragment(**m) for m in items_data]
                result = engine.analyze_cluster(cluster_id, items)
                if result:
                    audit_results.append(result.model_dump(mode='json'))
    else:
        provider = get_llm_provider(llm_provider, llm_model)
        engine = ContradictionEngine(provider)
        audit_results = []
        for cluster_id, items_data in clusters_data.items():
            items = [MemoryFragment(**m) for m in items_data]
            result = engine.analyze_cluster(cluster_id, items)
            if result:
                audit_results.append(result.model_dump(mode='json'))
    
    return audit_results

@DBOS.step()
def generate_report_step(audit_results_data: List[dict], raw_memories_data: List[dict]):
    """Step 4: Generate a Markdown report for human review."""
    print("Generating audit report...")
    if logfire:
        with logfire.span("generate_report_step"):
            audit_items = [AuditItem(**item) for item in audit_results_data]
            memories = [MemoryFragment(**m) for m in raw_memories_data]
            reporter.generate(audit_items, memories)
    else:
        audit_items = [AuditItem(**item) for item in audit_results_data]
        memories = [MemoryFragment(**m) for m in raw_memories_data]
        reporter.generate(audit_items, memories)
    return True

@DBOS.step()
def apply_automated_fixes_step(audit_results_data: List[dict], adapter_type: str, source: str, redundancy_action: str = "archive") -> dict:
    """Step 5: Apply automated fixes back to the store."""
    print(f"Applying automated fixes ({redundancy_action})...")
    if logfire:
        with logfire.span("apply_automated_fixes_step", action=redundancy_action):
            audit_items = [AuditItem(**item) for item in audit_results_data]
            adapter = get_adapter(adapter_type, source)
            handler = ExecutionHandler(adapter, redundancy_action=redundancy_action)
            res = handler.execute_batch(audit_items)
    else:
        audit_items = [AuditItem(**item) for item in audit_results_data]
        adapter = get_adapter(adapter_type, source)
        handler = ExecutionHandler(adapter, redundancy_action=redundancy_action)
        res = handler.execute_batch(audit_items)
    return res

@DBOS.workflow()
def ama_audit_workflow(adapter_type: str, source: str, llm_provider: str, llm_model: str, redundancy_action: str = "archive"):
    """Orchestrate the full audit pipeline with durable execution."""
    # 1. Fetch
    raw_memories = fetch_memories_step(adapter_type, source)
    
    # 2. Cluster
    clusters = cluster_memories_step(raw_memories)
    
    # 3. Analyze
    audit_report = analyze_clusters_step(clusters, llm_provider, llm_model)

    # 4. Report
    generate_report_step(audit_report, raw_memories)

    # 5. Execute
    execution_results = apply_automated_fixes_step(audit_report, adapter_type, source, redundancy_action=redundancy_action)
    
    return {"audit_report": audit_report, "execution_results": execution_results}

def run_audit(adapter_type: str, source: str, llm_provider: str, llm_model: str, redundancy_action: str = "archive"):
    DBOS.launch()
    try:
        results = ama_audit_workflow(adapter_type, source, llm_provider, llm_model, redundancy_action=redundancy_action)
        return results
    finally:
        pass
