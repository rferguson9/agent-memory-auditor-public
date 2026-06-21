# Agentic Memory Auditor (AMA)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

AMA is a decoupled, asynchronous, data-governance pipeline designed to act as a **Linter and Database Administrator** for agentic memory states.

Instead of running inline during live conversational loops (which introduces high latency and expensive API token costs), AMA scans your agent's underlying memory databases out-of-band. It cleans up redundant verbal bloat, compiles semantic structure reports, and flags logical human preference shifts for safe **Human-in-the-Loop (HITL)** resolution.

---

## The 3 Architectural Pillars

1. **Framework-Agnostic Ingestion:** Point AMA at any underlying database (SQLite, Postgres/pgvector, JSON) or existing memory framework (Mem0, LangGraph, ChromaDB) via highly structured, deterministic adapters.
2. **Human-in-the-Loop Arbitration:** Avoid silent database corruption. When AMA detects logical preference shifts (e.g., a developer switching from Python to Rust over a six-month window), it generates an interactive markdown dashboard (`docs/AUDIT_STAGING.md`) for explicit human triaging.
3. **Mitigating the "Natural Language Tax":** Chatty, loose conversational text logs bloat your vector retrievals and context windows. AMA continuously compresses verbose textual memory into machine-optimized JSON and compact key-value payloads.

---

## Core Philosophy: Cross-Layer Memory Governance

To build a self-healing, production-grade memory architecture, you must run **both** compression and contradiction detection across **both** episodic and semantic memory boundaries. AMA is engineered to govern this exact matrix out-of-band:

| Memory Layer | Contradiction Audits | Compression Engine |
| :--- | :--- | :--- |
| **Episodic** (Chronological Event Streams) | **Temporal Drift Detection:** Scans chronological timelines to identify when user preferences have shifted over time (e.g., Python on Day 1 vs. Rust on Day 180). | **Timeline Summarization:** Condenses chat-by-chat transcripts or tool trace blocks into a single high-level event summary, preserving history while shedding 90% of the token tax. |
| **Semantic** (Structured Facts & Knowledge) | **Factual Consistency Audits:** Scans files/JSON to prevent conflicting rules (e.g., `File A: Light Mode` and `File B: Dark Mode`) from polluting prompts and confusing the LLM. | **Natural Language Tax Pruning:** Strips loose, chatty conversational prose into hyper-dense, machine-optimized JSON, cutting retrieval context sizes by up to 80%. |

---

### 1. Episodic Memory (The "What Happened")
Episodic memory is a sequential, transaction-style record of user interactions (e.g., raw conversation logs, tool execution traces).

* **Episodic Contradictions (Temporal Drift):** Over months of usage, a user's workflow naturally drifts. By running contradiction audits over the sequential timeline, AMA isolates active changes of mind, flags stale actions, and stages them for safe, Human-in-the-Loop (HITL) arbitration before older data is overwritten.
* **Episodic Compression (Event Summarization):** Keeping every raw sentence in your database forever is financially unsustainable and dilutes retrievals. AMA rolls up sequential conversation transcripts into compact, chronological summaries:
  * *Raw:* "User spent Monday debugging database connection issues..." -> "User successfully connected the Postgres driver on Wednesday..."
  * *Compressed:* `"Week of June 20: User resolved a PostgreSQL connection pool bug."`

---

### 2. Semantic Memory (The "What is True")
Semantic memory represents the agent's general knowledge base—explicit facts, rules, and user preferences (e.g., favorite tools, layout configs).

* **Semantic Contradictions (Fact Collisions):** Storing facts across separate files or nested JSON blocks inevitably leads to conflicting configurations. If an LLM receives contradictory rules in its system prompt, it freezes or hallucinates. AMA scans these files to maintain a single, trusted "source of truth."
* **Semantic Compression (Prose Stripping):** Human preferences are usually captured via conversational speech, which contains heavy verbal fluff. AMA converts wordy descriptions into hyper-dense structures:
  * *Conversational:* *"The user spent ten minutes explaining how they absolutely prefer using JetBrains Mono typeface because they find it reduces eye strain..."*
  * *Compressed JSON:* `{"editor": {"font": "JetBrains Mono"}}` *(saving up to 85% in input tokens).*

---

### 3. The Time-Series Alignment
Agent memory is not a static database relation—it is a **semantic time-series stream**. Every user interaction, workflow preference, and factoid is a temporal data point that evolves.
* **The Problem:** Without pattern consistency, retrieving raw, chronological memory logs introduces semantic noise. If a retrieval query fetches three outdated preferences alongside one newly declared preference, the LLM struggle to isolate the true "current state" signal from the noise.
* **The AMA Solution:** Pointing to time-series database foundations, AMA audits historical data streams for trend consistency. It aligns sequential changes, isolates logical preference drift, and ensures that older temporal signals are gracefully decayed or archived while the current state is kept clear and prominent.

### 4. The Operational Mandate: Why Compression is Critical
Storing memory as loose, conversational prose imposes a severe operational tax on production agent architectures. Enforcing dense compression directly resolves three core engineering bottlenecks:
* **Token Cost Reduction (ROI):** Raw conversational memories (e.g., *"The user mentioned that they are currently building their backend service in Python using FastAPI because it is fast..."*) are highly wordy. Compressing them into machine-optimized JSON structures (e.g., `{"backend": "FastAPI", "lang": "Python"}`) slashes downstream retrieval prompt sizes by **up to 80%**, dramatically reducing live API billing.
* **Latency Optimization:** Verbose, unformatted prompts degrade model execution speed. Providing structured, dense JSON context guarantees faster Time-To-First-Token (TTFT) and significantly snappier agent chat responses.
* **Context Attention & Focus:** LLMs exhibit "Lost in the Middle" syndrome, losing track of details in long, descriptive contexts. Compact, hyper-dense payloads ensure the model's self-attention remains hyper-focused on high-signal facts rather than structural prose.

---

## System Architecture

```
                       ┌────────────────────────┐
                       │ Live Conversation Loop │
                       └───────────┬────────────┘
                                   │
                                   ▼ (Asynchronous Writes)
                       ┌────────────────────────┐
                       │  Raw Memory Database   │
                       │  (SQLite, JSON, etc.)  │
                       └───────────┬────────────┘
                                   │
                                   ▼ (Asynchronous Sweep)
                       ┌────────────────────────┐
                       │  Agent Memory Auditor  │
                       └─────┬────────────┬─────┘
                             │            │
         (Automated Fixes) ──┘            └─── (Human-In-The-Loop)
                             ▼                        ▼
                   ┌───────────────────┐    ┌────────────────────┐
                   │ Optimized DB Sync │    │ AUDIT_STAGING.md   │
                   │ (Compress/Decay)  │    │ Contradiction Dashboard│
                   └───────────────────┘    └────────────────────┘
```

---

## Quick Start (Local Prototype)

AMA utilizes **`uv`** (the ultra-fast Python package installer) for zero-configuration, sandboxed local execution.

### 1. Installation & Environment Setup
Clone the repository and sync dependencies:
```bash
git clone https://github.com/rferguson9/agent-memory-auditor.git
cd agent-memory-auditor
uv sync
```

Set your LLM Provider API keys in your environment or a `.env` file (see `.env.example`):
```bash
export GEMINI_API_KEY="your-gemini-key-here"
```

### 2. Generate Mock "Memory Rot" Data
Run the generator script to create sample memory databases populated with verbosity, sensitive PII, and logical preference contradictions:
```bash
python scripts/generate_mock_data.py
```
*This will create `data/mock_memories.db` and `data/mock_memories.json`.*

### 3. Run the Memory Audit (SQLite Example)
Scan the mock SQLite database using the default high-reasoning Gemini provider:
```bash
uv run python main.py --source data/mock_memories.db --type sqlite
```
*(To audit the mock JSON log file instead, simply run: `uv run python main.py --source data/mock_memories.json --type json`)*

### Switching LLM Providers & Models
By default, AMA utilizes **Gemini** with smart defaults. You can switch to any other configured LLM provider (using keys defined in your `.env`) by passing the `--provider` and `--model` arguments:

```bash
# Audit using OpenAI (defaults to gpt-4.1 from config):
uv run python main.py --source data/mock_memories.db --type sqlite --provider openai

# Audit using Anthropic (Claude):
uv run python main.py --source data/mock_memories.db --type sqlite --provider anthropic

# Audit using Groq (free, high-speed cloud tier):
uv run python main.py --source data/mock_memories.db --type sqlite --provider groq

# Audit using a Local LLM (Ollama/vLLM running on your machine):
uv run python main.py --source data/mock_memories.db --type sqlite --provider local

# Override the default model name on the fly:
uv run python main.py --source data/mock_memories.db --type sqlite --provider gemini --model gemini-2.5-pro
```

### Swapping Sources (Framework-Agnostic Core)
SQLite is just one of many supported adapters. In a real production application, you can audit your vector stores or memory platforms by simply changing `--type` and `--source`:
```bash
# Audit a production pgvector PostgreSQL instance:
uv run python main.py --source "postgresql://user:password@localhost:5432/your_db" --type postgres

# Audit a local ChromaDB collection:
uv run python main.py --source "/path/to/chroma_db_dir" --type chroma

# Audit a user session in the Mem0 framework:
uv run python main.py --source "user_123" --type mem0
```

*To run with physical deletion of secondary redundant rows instead of archiving:*
```bash
uv run python main.py --source data/mock_memories.db --type sqlite --redundancy-action delete
```

### 4. Review Your Staging Dashboard
Open the newly generated **`docs/AUDIT_STAGING.md`** file in your editor. This represents your **Human-in-the-Loop Dashboard** which stages:
* **Contradictions:** Clear logical shifts (e.g., Python vs. Rust) staged for manual review.
* **Sensitive PII:** Passwords or SSNs flagged for immediate deletion.
* **Automated Compressions:** Highly condensed, machine-readable JSON proposals successfully updated in the source database.

---

## Auditing Your Own Memory Databases

Once you have verified the pipeline with the mock data, you can point AMA directly at your actual agent memory stores:

### 1. SQLite Database
Point to your local SQLite file containing your agentic memory table:
```bash
uv run python main.py --source /path/to/your/agent_memories.db --type sqlite
```

### 2. JSON Logs
Point to a flat-file array of serialized memory logs:
```bash
uv run python main.py --source /path/to/your/logs.json --type json
```

### 3. PostgreSQL (pgvector)
Pass your relational connection string directly:
```bash
uv run python main.py --source "postgresql://user:password@localhost:5432/your_db" --type postgres
```

### 4. Production Vector Stores & Frameworks
* **ChromaDB:** Point to your local persistent vector database directory:
  ```bash
  uv run python main.py --source "/path/to/chroma_db_dir" --type chroma
  ```
* **Mem0 Framework:** Point to your active user session ID (assumes Mem0 API key is loaded in `.env`):
  ```bash
  uv run python main.py --source "user_123" --type mem0
  ```

### 5. PydanticAI (Serialized Conversation Logs)
PydanticAI represents conversation histories as nested lists of structured `ModelMessage` objects. To audit these logs, export your agent's active message history to a JSON file:

```python
import json

# Export your PydanticAI messages to a file
with open("pydantic_ai_history.json", "w") as f:
    f.write(result.new_messages_json().decode())
```

Then point AMA at that JSON file using the `pydantic_ai` type:
```bash
uv run python main.py --source pydantic_ai_history.json --type pydantic_ai
```

### 6. LangGraph (Shared Memory Store)
For frameworks like **LangGraph** that manage shared long-term memory via a memory `store` object, you can import and run AMA's adapters programmatically inside your own Python background scripts/workers:

```python
from langgraph.store.memory import InMemoryStore
from src.adapters.langgraph_adapter import LangGraphAdapter
from src.engine.execution import ExecutionHandler

# 1. Access your active LangGraph memory store and wrap it in the adapter
store = InMemoryStore()
adapter = LangGraphAdapter(store=store, namespace=("memories", "user_123"))

# 2. Run your out-of-band audit sweeps asynchronously
memories = adapter.fetch_memories()

# 3. Apply automated compressions back to the LangGraph store
# (This updates the store via .put() to keep your shared memory clean)
```

---

## Observability with Pydantic Logfire

AMA features native, zero-configuration support for **Pydantic Logfire**. Because AMA's data models (`MemoryFragment`, `AuditItem`) inherit directly from Pydantic's `BaseModel`, Logfire automatically intercepts and traces validation speeds, serialization events, and workflow step latency.

### How to Enable Tracing:
1. Log in to your Logfire account and authenticate your CLI locally:
   ```bash
   uv run logfire auth
   ```
2. Run any standard AMA command. Traces, performance metrics, and model validation logs will automatically stream to your Logfire web console in real-time:
   ```bash
   uv run python main.py --source data/mock_memories.db --type sqlite
   ```

---

## Supported Ecosystem & Adapters

AMA includes standard, built-in database, framework, and observability integrations:
* **Relational/Vector:** SQLite, PostgreSQL (with pgvector support), ChromaDB
* **Agentic Frameworks:** PydanticAI (Native ingestion of structured `ModelMessage` histories), Mem0, LangGraph Shared Store
* **Observability & Tracing:** Pydantic Logfire (Native, zero-config distributed tracing of validation models and steps)
* **LLM Providers:** Gemini (Default), OpenAI, Anthropic, Groq, and Local (Ollama/vLLM)

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
