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
# ]
# ///

"""
Inspect the Data Analyst agent's memory (conversation summary).

Usage:
    uv run examples/inspect_memory.py
"""

import asyncio
import os
import sys
import uuid

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages"))

load_dotenv()


async def main():
    from agents.data_analyst import create_data_analyst
    import numpy as np
    import pandas as pd
    import tempfile

    # Create a sample dataset
    rng = np.random.default_rng(42)
    n = 200
    df = pd.DataFrame({
        "passenger_id": range(1, n + 1),
        "age": np.round(rng.normal(30, 12, n), 1).clip(1, 80),
        "fare": np.round(rng.exponential(50, n), 2),
        "sex": rng.choice(["male", "female"], n),
        "survived": rng.integers(0, 2, n),
    })
    path = os.path.join(tempfile.gettempdir(), "chu_memory_test.csv")
    df.to_csv(path, index=False)

    agent = create_data_analyst()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("=" * 60)
    print("Inspect Agent Memory")
    print("=" * 60)
    print()

    # --- Round 1 ---
    q1 = f"Describe {path}"
    print(f"[1] User: {q1}")
    result = await agent.run(q1, config=config)
    print(f"    Agent: {result.content[:120]}...")
    print()

    # Inspect memory after round 1
    summary = await agent.get_memory(thread_id)
    print(f"[Memory after Q1]:")
    print(f"  {summary}")
    print()

    # --- Round 2 ---
    q2 = f"Show stats for the 'fare' column in {path}"
    print(f"[2] User: {q2}")
    result = await agent.run(q2, config=config)
    print(f"    Agent: {result.content[:120]}...")
    print()

    # Inspect memory after round 2
    summary = await agent.get_memory(thread_id)
    print(f"[Memory after Q2]:")
    print(f"  {summary}")
    print()

    # --- Round 3: Follow-up without dataset path (memory should remember it) ---
    q3 = "How many columns does the dataset have?"
    print(f"[3] User: {q3}")
    result = await agent.run(q3, config=config)
    print(f"    Agent: {result.content}")
    print()

    # Inspect memory after round 3
    summary = await agent.get_memory(thread_id)
    print(f"[Memory after Q3]:")
    print(f"  {summary}")
    print()

    # --- Full state ---
    state = await agent.get_full_state(thread_id)
    print(f"[Full state keys]: {list(state.keys()) if state else 'None'}")
    print(f"[Message count]:   {len(state['messages']) if state else 'N/A'}")


if __name__ == "__main__":
    asyncio.run(main())
