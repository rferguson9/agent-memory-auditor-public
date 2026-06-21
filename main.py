import sys
import argparse
from src.main_workflow import run_audit

from src.helpers.config import Settings

# Optional Pydantic Logfire Tracing Integration
try:
    import logfire
    # Only configure if a project token or direct local execution is initialized
    logfire.configure(pydantic_plugin=logfire.PydanticPlugin(record="all"))
    logfire.instrument_pydantic()
    print("🔥 Pydantic Logfire: Tracing & model instrumentation enabled.")
except Exception as e:
    # Fail silently if logfire is not installed or raises config errors
    pass

def main():
    settings = Settings()
    parser = argparse.ArgumentParser(description="Agentic Memory Auditor (AMA)")
    parser.add_argument("--source", type=str, required=True, help="Path to the memory source (JSON or DB file)")
    parser.add_argument("--type", type=str, required=True, choices=["json", "sqlite", "postgres", "mem0", "chroma", "langgraph", "pydantic_ai"], help="Type of adapter to use")
    parser.add_argument("--provider", type=str, default="gemini", choices=["gemini", "openai", "groq", "local", "anthropic"], help="LLM provider (default: gemini)")
    parser.add_argument("--model", type=str, default=None, help="LLM model name (defaults to Settings value)")
    parser.add_argument("--redundancy-action", type=str, default="archive", choices=["archive", "delete"], help="Action for secondary redundant memories after compression (default: archive)")

    args = parser.parse_args()

    # Use Settings as fallback for model if not provided via CLI
    if args.model is None:
        model_map = {
            "gemini": settings.gemini_model_name,
            "openai": settings.open_ai_model_name,
            "groq": settings.groq_model_name,
            "local": settings.local_model_name,
            "anthropic": settings.anthropic_model_name
        }
        args.model = model_map.get(args.provider)

    print(f"🚀 Starting Agentic Memory Audit on {args.source}...")
    print(f"🤖 Provider: {args.provider} | Model: {args.model} | Redundancy Action: {args.redundancy_action}")

    
    results = run_audit(args.type, args.source, args.provider, args.model, redundancy_action=args.redundancy_action)
    
    print("\n✅ Audit Cycle Complete.")
    print(f"Staged Fixes: {results['execution_results'].get('processed', 0)}")
    print("Review docs/AUDIT_STAGING.md for Human-in-the-Loop items.")

if __name__ == "__main__":
    main()
