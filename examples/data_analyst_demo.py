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
Data Analyst Agent — interactive REPL.

Usage:
    uv run examples/data_analyst_demo.py

You will be prompted to enter:
    1. The path to a dataset (CSV, Excel, Parquet, etc.)
    2. Your question/prompt for the agent

The conversation history is preserved across turns.
Type 'exit', 'quit', or '/bye' to stop.
Type '/new' to switch to a different dataset.
"""

import asyncio
import os
import sys
import uuid

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages"))

load_dotenv()


def make_sample_dataset() -> str:
    """Create a sample dataset and return its path."""
    import numpy as np
    import pandas as pd
    import tempfile

    rng = np.random.default_rng(42)
    n = 200
    df = pd.DataFrame({
        "passenger_id": range(1, n + 1),
        "name": [f"Passenger_{i}" for i in range(1, n + 1)],
        "age": np.round(rng.normal(30, 12, n), 1).clip(1, 80),
        "fare": np.round(rng.exponential(50, n), 2),
        "sex": rng.choice(["male", "female"], n),
        "embarked": rng.choice(["S", "C", "Q"], n, p=[0.6, 0.3, 0.1]),
        "survived": rng.integers(0, 2, n),
        "class": rng.choice(["First", "Second", "Third"], n, p=[0.2, 0.3, 0.5]),
    })
    df.loc[rng.choice(n, 10), "age"] = None
    path = os.path.join(tempfile.gettempdir(), "chu_demo.csv")
    df.to_csv(path, index=False)
    return path


async def repl():
    from agents.data_analyst import create_data_analyst

    agent = create_data_analyst()
    thread_id = str(uuid.uuid4())

    print("=" * 60)
    print("  Data Analyst Agent — Interactive REPL")
    print("=" * 60)
    print()
    print("  Commands:")
    print("    exit / quit / /bye    — stop")
    print("    /new                  — start a fresh conversation")
    print()

    dataset_path = ""
    first = True

    while True:
        # --- Dataset path ---
        if first or not dataset_path:
            default = make_sample_dataset() if first else dataset_path
            prompt_text = f"Dataset path (Enter for default: {os.path.basename(default)}): "
            inp = input(prompt_text).strip()
            dataset_path = inp if inp else default
            first = False
            print(f"  Using: {dataset_path}")
            print()

        # --- Question ---
        inp = input("Prompt > ").strip()

        if inp.lower() in ("exit", "quit", "/bye"):
            print("Goodbye!")
            break
        if inp.lower() == "/new":
            dataset_path = ""
            thread_id = str(uuid.uuid4())
            print("Starting a new conversation.")
            print()
            continue
        if not inp:
            continue

        # Prepend the dataset path to the prompt so the agent knows where the data is
        full_prompt = (
            f"[Dataset: {dataset_path}]\n{inp}"
            if dataset_path not in inp
            else inp
        )

        print("-" * 50)
        print("Agent: ", end="", flush=True)
        response_lines = []
        async for token in agent.astream(
            full_prompt,
            config={"configurable": {"thread_id": thread_id}},
        ):
            print(token, end="", flush=True)
            response_lines.append(token)
        print()
        # If the response contains a chart path, highlight it
        full = "".join(response_lines)
        if "Chart saved:" in full:
            for line in full.split("\n"):
                if "Chart saved:" in line:
                    print(f"  -> {line.strip()}")
        print()


if __name__ == "__main__":
    asyncio.run(repl())
