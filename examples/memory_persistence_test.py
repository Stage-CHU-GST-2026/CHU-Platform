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
Postgres persistence test — memory survives across agent restarts.

Usage:
    uv run examples/memory_persistence_test.py
"""

import asyncio
import os
import sys
import uuid

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages"))

load_dotenv()


async def main():
    import numpy as np
    import pandas as pd
    import tempfile

    from agents.data_analyst.memory import PostgresConfig, create_checkpointer
    # Credentials come from .env (MEMORY_DATABASE_URL or DATABASE_URL)

    rng = np.random.default_rng(42)
    n = 200
    df = pd.DataFrame({
        "passenger_id": range(1, n + 1),
        "age": np.round(rng.normal(30, 12, n), 1).clip(1, 80),
        "fare": np.round(rng.exponential(50, n), 2),
        "sex": rng.choice(["male", "female"], n),
        "survived": rng.integers(0, 2, n),
    })
    path = os.path.join(tempfile.gettempdir(), "chu_persist_test.csv")
    df.to_csv(path, index=False)

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("=" * 60)
    print("  Postgres Persistence Test")
    print("=" * 60)
    print(f"  Thread ID: {thread_id}")
    print()

    # ── Session 1: Ask a question ────────────────────────────────────
    print("── [Session 1] ──")
    async with create_checkpointer(PostgresConfig()) as cp:
        from agents.data_analyst import create_data_analyst
        agent = create_data_analyst(checkpointer=cp)

        q1 = f"Describe {path}"
        print(f"  Q: {q1}")
        result = await agent.run(q1, config=config)
        print(f"  A: {result.content[:100]}...")
        summary = await agent.get_memory(thread_id)
        print(f"  📝 Memory: {summary}")
    print()

    # ── Session 2: New agent instance, same thread — should remember ─
    print("── [Session 2] (new agent, same thread) ──")
    async with create_checkpointer(PostgresConfig()) as cp:
        from agents.data_analyst import create_data_analyst
        agent2 = create_data_analyst(checkpointer=cp)

        q2 = "What did I ask about before?"
        print(f"  Q: {q2}")
        result = await agent2.run(q2, config=config)
        print(f"  A: {result.content[:200]}...")
        summary = await agent2.get_memory(thread_id)
        print(f"  📝 Memory: {summary}")
    print()

    print("✅ Postgres persistence verified!")
    print(f"  Thread ID: {thread_id}")


if __name__ == "__main__":
    asyncio.run(main())
