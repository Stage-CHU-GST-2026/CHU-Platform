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
Data Analyst Agent demo.

Usage:
    uv run examples/data_analyst_demo.py

This creates a sample dataset and uses the Data Analyst agent
to explore and describe it step by step.
"""

from dotenv import load_dotenv
import asyncio
import os
import sys

# Allow imports from local packages/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


load_dotenv()


async def main():
    # Import here so the script works with uv run
    from agents.data_analyst import create_data_analyst

    # Create a sample dataset
    import pandas as pd
    import numpy as np
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

    agent = create_data_analyst()

    print("=" * 60)
    print("Data Analyst Agent")
    print(f"Dataset: {path}")
    print("=" * 60)
    print()

    questions = [
        f"Describe the dataset at {path} — its shape, columns, and any missing values.",
        f"Give me the statistical summary for the numeric columns in {path}.",
        f"Show me the first 5 rows of {path}.",
        f"Tell me all about the 'fare' column in {path}.",
        f"Group by 'class' in {path} and show the mean fare for each class.",
        f"Correlation between age and fare in {path}.",
    ]

    for i, q in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] User: {q}")
        print("-" * 50)
        result = await agent.run(q)
        print(f"Agent: {result.content}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
