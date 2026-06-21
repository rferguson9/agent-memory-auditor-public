import os
import tempfile
import sqlite3
import json
from datetime import datetime
from src.adapters.json_adapter import JSONAdapter
from src.adapters.sqlite_adapter import SQLiteAdapter
from src.helpers.pydantic_models import MemoryFragment
from src.engine.execution import ExecutionHandler
from src.helpers.pydantic_models import AuditItem, ResolutionAction

def test_json_delete_and_archive():
    # Setup temporary JSON file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        temp_path = f.name
        
    initial_data = [
        {
            "memory_id": "mem_001",
            "user_id": "user_123",
            "timestamp": datetime.now().isoformat(),
            "raw_content": "Old verbose memory 1",
            "category": "workflow_preference",
            "access_count": 5,
            "last_accessed": datetime.now().isoformat()
        },
        {
            "memory_id": "mem_002",
            "user_id": "user_123",
            "timestamp": datetime.now().isoformat(),
            "raw_content": "Old verbose memory 2",
            "category": "workflow_preference",
            "access_count": 2,
            "last_accessed": datetime.now().isoformat()
        }
    ]
    
    with open(temp_path, "w") as f:
        json.dump(initial_data, f)
        
    try:
        adapter = JSONAdapter(temp_path)
        memories = adapter.fetch_memories()
        assert len(memories) == 2
        
        # Test delete memory_id 'mem_002'
        success = adapter.delete_memory("mem_002")
        assert success is True
        
        mem_after_delete = adapter.fetch_memories()
        assert len(mem_after_delete) == 1
        assert mem_after_delete[0].memory_id == "mem_001"
        
        # Test updating/archiving 'mem_001'
        success_update = adapter.update_memory("mem_001", {"category": "archived_workflow_preference"})
        assert success_update is True
        
        mem_after_archive = adapter.fetch_memories()
        assert mem_after_archive[0].category == "archived_workflow_preference"
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_sqlite_delete_and_archive():
    # Setup temporary SQLite file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_path = f.name
        
    try:
        adapter = SQLiteAdapter(temp_path)
        
        # Insert initial test records
        with sqlite3.connect(temp_path) as conn:
            cursor = conn.cursor()
            now_str = datetime.now().isoformat()
            cursor.execute(
                f"INSERT INTO {adapter.table_name} (memory_id, user_id, timestamp, raw_content, category, access_count, last_accessed) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("mem_001", "user_123", now_str, "SQLite memory 1", "workflow_preference", 5, now_str)
            )
            cursor.execute(
                f"INSERT INTO {adapter.table_name} (memory_id, user_id, timestamp, raw_content, category, access_count, last_accessed) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("mem_002", "user_123", now_str, "SQLite memory 2", "workflow_preference", 2, now_str)
            )
            conn.commit()
            
        memories = adapter.fetch_memories()
        assert len(memories) == 2
        
        # Test delete memory_id 'mem_002'
        success = adapter.delete_memory("mem_002")
        assert success is True
        
        mem_after_delete = adapter.fetch_memories()
        assert len(mem_after_delete) == 1
        assert mem_after_delete[0].memory_id == "mem_001"
        
        # Test archiving category
        success_update = adapter.update_memory("mem_001", {"category": "archived_workflow_preference"})
        assert success_update is True
        
        mem_after_archive = adapter.fetch_memories()
        assert mem_after_archive[0].category == "archived_workflow_preference"
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_execution_handler_delete():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        temp_path = f.name
        
    initial_data = [
        {
            "memory_id": "mem_001",
            "user_id": "user_123",
            "timestamp": datetime.now().isoformat(),
            "raw_content": "Old verbose memory 1",
            "category": "workflow_preference",
            "access_count": 5,
            "last_accessed": datetime.now().isoformat()
        },
        {
            "memory_id": "mem_002",
            "user_id": "user_123",
            "timestamp": datetime.now().isoformat(),
            "raw_content": "Old verbose memory 2",
            "category": "workflow_preference",
            "access_count": 2,
            "last_accessed": datetime.now().isoformat()
        }
    ]
    
    with open(temp_path, "w") as f:
        json.dump(initial_data, f)
        
    try:
        adapter = JSONAdapter(temp_path)
        
        # Scenario: execution handler runs with 'delete' option
        handler = ExecutionHandler(adapter, redundancy_action="delete")
        
        audit_items = [
            AuditItem(
                cluster_id="workflow_preference",
                target_topic="Backend language preference",
                action_required=ResolutionAction.AUTOMATIC_COMPRESS,
                justification="Testing compression deletion",
                affected_memory_ids=["mem_001", "mem_002"],
                optimized_payload_proposal="Compressed Payload Content"
            )
        ]
        
        results = handler.execute_batch(audit_items)
        assert results["processed"] == 1
        assert results["errors"] == 0
        
        # After execution: mem_001 should be updated, mem_002 should be physically deleted
        memories = adapter.fetch_memories()
        assert len(memories) == 1
        assert memories[0].memory_id == "mem_001"
        assert memories[0].raw_content == "Compressed Payload Content"
        assert memories[0].category == "workflow_preference_optimized"
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_execution_handler_archive():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        temp_path = f.name
        
    initial_data = [
        {
            "memory_id": "mem_001",
            "user_id": "user_123",
            "timestamp": datetime.now().isoformat(),
            "raw_content": "Old verbose memory 1",
            "category": "workflow_preference",
            "access_count": 5,
            "last_accessed": datetime.now().isoformat()
        },
        {
            "memory_id": "mem_002",
            "user_id": "user_123",
            "timestamp": datetime.now().isoformat(),
            "raw_content": "Old verbose memory 2",
            "category": "workflow_preference",
            "access_count": 2,
            "last_accessed": datetime.now().isoformat()
        }
    ]
    
    with open(temp_path, "w") as f:
        json.dump(initial_data, f)
        
    try:
        adapter = JSONAdapter(temp_path)
        
        # Scenario: execution handler runs with default 'archive' option
        handler = ExecutionHandler(adapter, redundancy_action="archive")
        
        audit_items = [
            AuditItem(
                cluster_id="workflow_preference",
                target_topic="Backend language preference",
                action_required=ResolutionAction.AUTOMATIC_COMPRESS,
                justification="Testing compression archiving",
                affected_memory_ids=["mem_001", "mem_002"],
                optimized_payload_proposal="Compressed Payload Content"
            )
        ]
        
        results = handler.execute_batch(audit_items)
        assert results["processed"] == 1
        
        # After execution: mem_001 updated, mem_002 category updated to archived_workflow_preference
        memories = adapter.fetch_memories()
        assert len(memories) == 2
        
        # Verify first is updated and optimized
        mem_001_ret = next(m for m in memories if m.memory_id == "mem_001")
        assert mem_001_ret.raw_content == "Compressed Payload Content"
        assert mem_001_ret.category == "workflow_preference_optimized"
        
        # Verify second is archived
        mem_002_ret = next(m for m in memories if m.memory_id == "mem_002")
        assert mem_002_ret.category == "archived_workflow_preference"
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
