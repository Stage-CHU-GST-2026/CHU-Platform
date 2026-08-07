# /// script
# dependencies = [
#   "langchain>=0.3.0",
#   "langchain-openai>=1.3.5",
#   "langgraph>=1.2.9",
#   "python-dotenv>=1.0.0",
#   "pandas>=2.0.0",
#   "numpy>=1.24.0",
#   "matplotlib>=3.7.0",
#   "pyyaml>=6.0",
#   "psycopg[binary,pool]>=3.2",
#   "langgraph-checkpoint-postgres>=2.0",
# ]
# ///

"""
Pluggable memory demo — run the same agent with InMemory or Postgres.

Usage:
  # In-memory (default)
  uv run examples/memory_demo.py

#   # Postgres (requires postgres container — see docker-compose.yaml)
  uv run examples/memory_demo.py --postgres
"""

import argparse
import asyncio
import os
import sys
import uuid

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages"))

load_dotenv()


async def main():
    parser = argparse.ArgumentParser(description="Pluggable memory demo")
    parser.add_argument(
        "--postgres",
        action="store_true",
        help="Use Postgres memory instead of InMemory",
    )
    parser.add_argument(
        "--store",
        action="store_true",
        help="Also enable long-term memory store (Postgres only)",
    )
    args = parser.parse_args()

    from agents.data_analyst import create_data_analyst
    import numpy as np
    import pandas as pd
    import tempfile

    # ── Create sample dataset ────────────────────────────────────────
    rng = np.random.default_rng(42)
    n = 200
    df = pd.DataFrame({
        "passenger_id": range(1, n + 1),
        "age": np.round(rng.normal(30, 12, n), 1).clip(1, 80),
        "fare": np.round(rng.exponential(50, n), 2),
        "sex": rng.choice(["male", "female"], n),
        "survived": rng.integers(0, 2, n),
        "class": rng.choice(["First", "Second", "Third"], n, p=[0.2, 0.3, 0.5]),
    })
    df.loc[rng.choice(n, 10), "age"] = None
    path = os.path.join(tempfile.gettempdir(), "chu_memory_demo.csv")
    df.to_csv(path, index=False)

    # ── Build memory ─────────────────────────────────────────────────
    memory_type = "PostgreSQL" if args.postgres else "InMemory"
    print("=" * 60)
    print(f"  Data Analyst Agent — {memory_type} Memory")
    print("=" * 60)
    print()

    if args.postgres:
        from agents.data_analyst.memory import PostgresConfig, create_checkpointer, create_store

        pg_config = PostgresConfig(enable_store=args.store)
        async with (
            create_checkpointer(pg_config) as checkpointer,
            create_store(pg_config if args.store else None) as store,
        ):
            agent = create_data_analyst(
                checkpointer=checkpointer,
                store=store,
            )
            await run_conversation(agent, path, memory_type)
    else:
        agent = create_data_analyst()
        await run_conversation(agent, path, memory_type)

    print("Done.")


async def run_conversation(
    agent,
    dataset_path: str,
    memory_type: str,
):
    """Run a multi-turn conversation and inspect memory after each turn."""
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    questions = [
        f"Describe the dataset at {dataset_path} — shape, columns, missing values.",
        f"Give me the statistical summary of the 'fare' column in {dataset_path}.",
        "How many columns does the dataset have?",  # relies on memory
    ]

    for i, q in enumerate(questions, 1):
        print(f"[Q{i}] User: {q[:70]}...")
        result = await agent.run(q, config=config)
        # Show first ~150 chars of the response
        preview = result.content[:150].replace("\n", " ")
        print(f"     Agent: {preview}...")
        print()

        # Inspect memory
        summary = await agent.get_memory(thread_id)
        if summary:
            print(f"     📝 Memory: {summary}")
        print()

    print(f"  ── Thread ID: {thread_id} ──")


if __name__ == "__main__":
    asyncio.run(main())
